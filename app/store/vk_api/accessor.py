import typing
from typing import Optional
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message
from app.store.vk_api.poller import Poller
from app.store.vk_api.dataclasses import Update, UpdateObject, UpdateMessage

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session = ClientSession()
        await self.get_group_id()
        await self._get_long_poll_service()
        self.poller = Poller(app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        await self.session.close()
        await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def get_group_id(self):
        params = {
            "access_token": self.app.config.bot.token,
            "v": "5.131"
        }
        url = self._build_query(
            "https://api.vk.com/method/",
            "groups.getById",
            params
        )
        group_id_request = await self.session.get(url)
        group_json = await group_id_request.json()
        group_id = group_json['response'][0]["id"]
        self.app.config.bot.group_id = group_id

    async def _get_long_poll_service(self):
        params = {
            "access_token": self.app.config.bot.token,
            "group_id": self.app.config.bot.group_id
        }
        url = self._build_query(
            "https://api.vk.com/method/",
            "groups.getLongPollServer",
            params
        )
        long_poll_request = await self.session.get(url)
        long_poll_json = await long_poll_request.json()
        self.key = long_poll_json["response"]["key"]
        self.server = long_poll_json["response"]["server"]
        self.ts = long_poll_json["response"]["ts"]

    async def poll(self):
        params = {
            "act": "a_check",
            "key": self.key,
            "ts": self.ts,
            "wait": 10
        }
        url = self._build_query(
            "https://lp.vk.com/wh218882125",
            "",
            params
        )
        long_poll_request = await self.session.get(url)
        long_poll_json = await long_poll_request.json()
        raw_updates = []
        updates = []
        for i in long_poll_json["updates"]:
            if i["type"] != "message_typing_state":
                raw_updates.append(i)

        for update in raw_updates:
            updates.append(
                Update(
                    type=update["type"],
                    object=UpdateObject(
                        message=UpdateMessage(
                            from_id=update["object"]["message"]["from_id"],
                            text=update["object"]["message"]["text"],
                            id=update["object"]["message"]["id"]
                        )
                    )
                )
            )

        return updates

    async def send_message(self, message: Message) -> None:
        params = {"access_token": self.app.config.bot.token, "user_id": message.user_id, "message": message.text}
        url = self._build_query("https://api.vk.com/method/", "messages.send", params)
        send_message_request = self.session.post(url)
