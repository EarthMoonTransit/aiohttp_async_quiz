from aiohttp_session import new_session, get_session
from app.web.app import View
from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import docs, request_schema, response_schema
from app.admin.schemes import AdminSchema
from app.web.mixins import login_required
from app.web.schemes import OkResponseSchema
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["admin"], summary="Admin login", description="Administrator authorization")
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        data = self.request["data"]
        admin = await self.request.app.store.admins.get_by_email(data['email'])
        if admin:
            session = await new_session(request=self.request)
            session["admin_id"] = admin.id
            session["admin_email"] = admin.email
            return json_response(data={"id": admin.id, "email": admin.email})
        else:
            raise HTTPForbidden


class AdminCurrentView(View):
    @docs(tags=["admin"], summary="Admin current", description="Output of the current administrator")
    @response_schema(OkResponseSchema, 200)
    @login_required
    async def get(self):
        session = await get_session(self.request)
        return json_response(
            data={
                "id": session["admin_id"],
                "email": session["admin_email"]
            }
        )


