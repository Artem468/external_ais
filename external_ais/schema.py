import json

import graphene
from django.db.models import Q
from graphene.types.generic import GenericScalar
from graphene_django import DjangoObjectType

from core.models import User, Request


class UserType(DjangoObjectType):
    params = GenericScalar()

    class Meta:
        model = User
        fields = "__all__"


class RequestType(DjangoObjectType):
    params = GenericScalar()

    class Meta:
        model = Request
        fields = "__all__"


class JSONFilterInput(graphene.InputObjectType):
    key = graphene.String(required=True)
    value = graphene.String(required=True)
    operator = graphene.String(required=False, default_value="eq")


def apply_json_filters(qs, json_filters):
    """Универсальная функция для фильтрации JSON-полей"""
    if not json_filters:
        return qs

    q = Q()
    for f in json_filters:
        lookup = f"params__{f.key.replace('.', '__')}"
        if f.operator and f.operator != "eq":
            lookup += f"__{f.operator}"
        try:
            value = json.loads(f.value)
        except Exception:
            value = f.value

        q &= Q(**{lookup: value})

    return qs.filter(q)


class Query(graphene.ObjectType):
    users = graphene.List(
        UserType,
        username=graphene.String(),
        params_filter=graphene.List(JSONFilterInput),
    )
    requests = graphene.List(
        RequestType,
        status=graphene.String(),
        params_filter=graphene.List(JSONFilterInput),
    )

    def resolve_users(self, info, username=None, params_filter=None):
        qs = User.objects.all()
        if username:
            qs = qs.filter(username__icontains=username)
        qs = apply_json_filters(qs, params_filter)
        return qs

    def resolve_requests(self, info, status=None, params_filter=None):
        qs = Request.objects.all()
        if status:
            qs = qs.filter(status=status)
        qs = apply_json_filters(qs, params_filter)
        return qs


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        params = GenericScalar(required=False)
        max_daily_requests = graphene.Int(required=False)

    user = graphene.Field(UserType)

    def mutate(self, info, username, password, params=None, max_daily_requests=None):
        user = User(
            username=username,
            params=params or {},
            max_daily_requests=max_daily_requests,
        )
        user.set_password(password)
        user.save()
        return CreateUser(user=user)


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        params = GenericScalar(required=False)
        max_daily_requests = graphene.Int(required=False)

    user = graphene.Field(UserType)

    def mutate(self, info, id, params=None, max_daily_requests=None):
        user = User.objects.get(id=id)
        if params is not None:
            user.params = params
        if max_daily_requests is not None:
            user.max_daily_requests = max_daily_requests
        user.save()
        return UpdateUser(user=user)


class CreateRequest(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=False)
        params = GenericScalar(required=False)
        text = graphene.String(required=False)
        status = graphene.String(required=False)

    request = graphene.Field(RequestType)

    def mutate(self, info, user_id=None, params=None, text=None, status="processed"):
        req = Request.objects.create(
            user_id=user_id, params=params or {}, text=text or "", status=status
        )
        return CreateRequest(request=req)


class UpdateRequest(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        params = GenericScalar(required=False)
        status = graphene.String(required=False)

    request = graphene.Field(RequestType)

    def mutate(self, info, id, params=None, status=None):
        req = Request.objects.get(id=id)
        if params is not None:
            req.params = params
        if status is not None:
            req.status = status
        req.save()
        return UpdateRequest(request=req)


class DeleteRequest(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        Request.objects.filter(id=id).delete()
        return DeleteRequest(ok=True)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    create_request = CreateRequest.Field()
    update_request = UpdateRequest.Field()
    delete_request = DeleteRequest.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
