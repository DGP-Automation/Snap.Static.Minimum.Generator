import requests
import xml.etree.ElementTree as ET
import os
import shutil


def avatar_skill_parser(skill: dict) -> str:
    try:
        if "Icon" in skill.keys():
            resource_name = skill["Icon"]
            if "skill" in resource_name.lower():
                return "Skill"
            elif "talent" in resource_name.lower():
                return "Talent"
            else:
                print(f"Unrecognized resource name: {resource_name}.")
    except (KeyError, AttributeError):
        raise RuntimeError(f"Error parsing skill: {skill}.")


def avatar_parser() -> list:
    AVATAR_METADATA_URL = "https://raw.githubusercontent.com/DGP-Studio/Snap.Metadata/main/Genshin/CHS/Avatar.json"
    return_list = []

    response = requests.get(AVATAR_METADATA_URL).json()
    for avatar in response:
        resource_dict = {
            "AvatarIcon": [avatar["Icon"], avatar["SideIcon"]],
            "Skill": [],
            "Talent": [],
        }

        # Skills
        for skill_group in avatar["SkillDepot"].keys():
            if skill_group == "Arkhe":
                continue
            if type(avatar["SkillDepot"][skill_group]) is list:
                for skill in avatar["SkillDepot"][skill_group]:
                    r = avatar_skill_parser(skill)
                    if r:
                        resource_dict[r].append(skill["Icon"])
            elif type(avatar["SkillDepot"][skill_group]) is dict:
                r = avatar_skill_parser(avatar["SkillDepot"][skill_group])
                if r:
                    resource_dict[r].append(avatar["SkillDepot"][skill_group]["Icon"])
            else:
                raise RuntimeError(f"Unrecognized skill group: {skill_group}.")
        return_list.append(resource_dict)

    return return_list


def is_useful_material(material: dict) -> bool:
    USEFUL_TYPES = ["角色天赋素材", "好感成长", "通用货币",
                    "武器强化素材", "系统开放", "素材",
                    "角色培养素材", "角色经验素材", "蒙德区域特产",
                    "须弥区域特产", "角色突破素材", "命之座激活",
                    "食材", "精炼材料", "稻妻区域特产",
                    "锻造用矿石", "摆设套装图纸", "武器突破素材",
                    "食物", "枫丹区域特产", "七国徽印",
                    "角色与武器培养素材", "摆设图纸", "璃月区域特产",
                    "挑战结算道具", "圣遗物强化素材", "冒险道具"
                    ]

    return material["TypeDescription"] in USEFUL_TYPES


def item_icon_parser() -> list:
    ITEM_METADATA_URL = "https://raw.githubusercontent.com/DGP-Studio/Snap.Metadata/main/Genshin/CHS/Material.json"
    return_list = []

    response = requests.get(ITEM_METADATA_URL).json()
    for material in response:
        if is_useful_material(material):
            return_list.append(material["Icon"] + ".png")

    return_list = list(set(return_list))

    return return_list


def emotion_icon_parser() -> list:
    EMOTION_METADATA_URL = ("https://raw.githubusercontent.com/DGP-Studio/Snap.Hutao/main/src/Snap.Hutao/Snap.Hutao"
                            "/Control/Theme/Uri.xaml")
    return_list = []

    response = requests.get(EMOTION_METADATA_URL).content
    with open('Uri.xaml', 'wb') as f:
        f.write(response)
    tree = ET.parse('Uri.xaml')
    root = tree.getroot()
    for child in root:
        icon_name = list(child.attrib.values())[0] + ".png"
        if icon_name.startswith("UI_EmotionIcon"):
            return_list.append(icon_name)
    return_list = list(set(return_list))
    return return_list


if __name__ == "__main__":
    materials_list = item_icon_parser()
    emotion_list = emotion_icon_parser()

    # process materials
    os.makedirs("./ItemIcon-Minimum", exist_ok=True)
    item_icon_file_list = os.listdir("./ItemIcon/")
    for f in item_icon_file_list:
        if f in materials_list:
            shutil.copy(f"./ItemIcon/{f}", f"./ItemIcon-Minimum/{f}")

    # process emotions
    os.makedirs("./EmotionIcon-Minimum", exist_ok=True)
    emotion_icon_file_list = os.listdir("./EmotionIcon/")
    for f in emotion_icon_file_list:
        if f in emotion_list:
            shutil.copy(f"./EmotionIcon/{f}", f"./EmotionIcon-Minimum/{f}")
