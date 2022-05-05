import requests
import json
import os
from datetime import date

class NotionWorker:
    def __init__(self):
        self.secret_token = None
        self.headers = None

    def set_headers(self):
        headers = {
            "Authorization": "Bearer " + self.secret_token,
            "Accept": "application/json",
            "Notion-Version": "2022-02-22",
            "Content-Type": "application/json"
        }
        self.headers = headers

    def query_db(self, database_id, db_filter=None, start_cursor=None):
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        payload = {"page_size": 100}

        if db_filter:
            payload["filter"] = db_filter

        if start_cursor:
            payload["start_cursor"] = start_cursor

        headers = self.headers
        response = requests.post(url, json=payload, headers=headers)
        db_json = json.loads(response.text)

        return db_json

    def notion_property_value_maker(self, property_type, content):
        switcher = {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                        "content": content
                        }
                    }
                ]
            },
            "url": {
                "url": content
            },
            "rich_text": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content
                        }
                    },
                ],
            },
            "date": {
                "date": {
                    "start": content
                }
            },
            "multi_select": {
                "multi_select": [{"name": tag} for tag in content]
            },
            "relation": {
                "relation": [
                    {
                        "id": content
                    }
                ]
            },
            "cover": {
                'type': 'external',
                'external': {'url': content}
            },
            "icon": {
                'type': 'external',
                'external': {'url': content}
            },
            "embed_video_link": [
                {
                    "type": "video",
                    "video": {
                        "type": "external",
                        "external": {
                            "url": content
                        }
                    }
                }
            ],
            "embed": [
                {
                    "type": "embed",
                    "embed": {
                        "url": content
                    }
                }
            ],
            "bookmark": [
                {
                    "type": "bookmark",
                    "bookmark": {
                        "caption":[],
                        "url": content
                    }
                }
            ],
        }

        return switcher.get(property_type)


class NotionCrawlerHandler(NotionWorker):
    def __init__(self):
        super().__init__()
        current_path = os.getcwd()
        notion_secret_name = "notion_secret.json"
        data_path = current_path + "/" + notion_secret_name
        file = open(data_path)
        file_dict = json.load(file)
        self.secret_token = file_dict["secret_token"]
        self.channel_database_id = file_dict["channel_database_id"]
        self.content_database_id = file_dict["content_database_id"]
        self.set_headers()

    def get_channel_list(self):
        db_json = self.query_db(self.channel_database_id)
        results_list = db_json["results"]
        channel_list = []
        for result in results_list:
            kind = result["properties"]["Kind"]["select"]["name"]
            url = result["properties"]["URL"]["url"]
            title = result["properties"]["Name"]["title"][0]["text"]["content"]
            subscribers = result["properties"]["subscriber"]["people"]
            channel_data_dict = {
                "kind": kind,
                "url": url,
                "title": title,
                "subscribers": subscribers
            }
            channel_list.append(channel_data_dict)

        return channel_list


    

    def get_channel_db(self, channel_id):
        db_filter = {
            "property": "channel_id",
            "rich_text": {
                "equals": channel_id
            }
        }
        db_json = self.query_db(self.channel_database_id, db_filter)
        
        return db_json

    def get_channel_relation_id(self, channel_id):
        db_json = self.get_channel_db(channel_id)
        channel_relation_id = db_json["results"][0]["id"]
        return channel_relation_id
    
    def get_channel_logo_link(self, channel_id):
        db_json = self.get_channel_db(channel_id)
        channel_logo_link = db_json["results"][0]['properties']["logo_link"]["url"]
        return channel_logo_link

    def make_insert_db_data(self, database_id, data):
        name = self.notion_property_value_maker("title", data["title"])
        content_url = self.notion_property_value_maker("url", data["content_url"])
        content_id = self.notion_property_value_maker("rich_text", data["content_id"])
        channel_url = self.notion_property_value_maker("url", data["channel_url"])
        channel_id = self.notion_property_value_maker("rich_text", data["channel_id"])
        img_link = self.notion_property_value_maker("url", data["img_link"])
        upload_at = self.notion_property_value_maker("date", data["upload_at"])
        description = self.notion_property_value_maker("rich_text", data["description"])
        tag_list = self.notion_property_value_maker("multi_select", data["tag_list"])
        cover = self.notion_property_value_maker("cover", data["img_link"])
        
        channel_relation = ""
        icon = ""
        try:
            channel_relation_id = self.get_channel_relation_id(data["channel_id"])
            channel_relation = self.notion_property_value_maker("relation", channel_relation_id)
            logo_link = self.get_channel_logo_link(data["channel_id"])
            icon = self.notion_property_value_maker("icon", logo_link)
        except Exception as error:
            print(repr(error))

        children = ""
        if "facebook" in data["content_url"]:
            children_block_tpye = "bookmark"
        elif "youtube" in data["content_url"]:
            children_block_tpye = "embed_video_link"
        children = self.notion_property_value_maker(children_block_tpye, data["content_url"])

        payload = {
            "parent": {
                "database_id": database_id,
            },
            "properties": {
                "Name": name,
                "content_url": content_url,
                "content_id": content_id,
                "channel_url": channel_url,
                "channel_id": channel_id,
                "img_link": img_link,
                "upload_at": upload_at,
                "description": description,
                "tag_list": tag_list,
                "channel_relation": channel_relation
            },
            "cover": cover,
            "icon": icon,
            "children": children
        }

        print(payload)
        
        return payload

    def write_content_data_list_to_db(self, content_data_list):
        exist_link_list = []
        has_more = True
        start_cursor = None
        while has_more:
            db_json = self.query_db(self.content_database_id, start_cursor=start_cursor)
            results = db_json["results"]
            exist_link_list += [result["properties"]["content_url"]["url"] for result in results]
            has_more = db_json["has_more"]
            start_cursor = db_json["next_cursor"]

        for data in content_data_list:
            if data["content_url"] in exist_link_list:
                print("===exist!===")
                print(data["content_url"])
            else:
                print("==update!===")
                print(data["content_url"])
                # payload = self.make_insert_db_data(self.content_database_id, data)
                url = "https://api.notion.com/v1/pages"
                headers = self.headers

                response = requests.post(url, json=payload, headers=headers)
                print(response.status_code)
                print(response.text)



class NotionDataTransfer():
    def __init__(self):
        pass

    def crawled_data_to_content_data_list(self, web_name, data_list):
        if web_name == "notion-youtube":
            content_data_list = self.youtube_data_transfer(data_list)
        elif web_name == "notion-FB":
            content_data_list = self.fb_data_transfer(data_list)
        
        return content_data_list

    def youtube_data_transfer(self, data_list):
        content_data_list = []
        for data in data_list:
            content_data = {}
            content_data["title"] = data["title"]
            content_data["channel_id"] = data["channel_id"]
            content_data["channel_url"] = data["channel_url"]
            content_data["content_id"] = data["video_id"]
            content_data["content_url"] = data["video_url"]
            content_data["upload_at"] = data["published"]
            content_data["img_link"] = data["img_link"]
            content_data["description"] = data["description"]
            content_data["tag_list"] = data["tag_list"]
            content_data_list.append(content_data)

        return content_data_list

    def fb_data_transfer(self, data_list):
        content_data_list = []
        for data in data_list:
            content_data = {}
            content_data["title"] = data["title"]
            content_data["channel_id"] = data["post_group_id"]
            content_data["channel_url"] = data["post_group_url"]
            content_data["content_id"] = data["post_link"].replace("www.facebook.com/","")
            content_data["content_url"] = data["post_link"]
            content_data["upload_at"] = data["post_time"]
            fb_link = "https://i.pinimg.com/550x/f7/99/20/f79920f4cb34986684e29df42ec0cebe.jpg"
            content_data["img_link"] = data["img_link"] or fb_link
            content_data["description"] = data["content"]
            content_data["tag_list"] = ""
            content_data_list.append(content_data)

        return content_data_list