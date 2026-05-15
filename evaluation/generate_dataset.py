"""Synthesize an arbitrarily large evaluation dataset with reliable ground truth.

Each row is built by composing a sentence/blob template with values drawn from
predefined pools (schools, companies, majors, titles, degrees, dates). The
ground truth is the parameter dict that produced the row — so labels are
guaranteed correct.

Usage:
    python evaluation/generate_dataset.py --n 1000 --out evaluation/eval_dataset_1000.json --seed 42

Categories produced (uniform random):
    nl-en-edu, nl-zh-edu, nl-en-work, nl-zh-work,
    blob-en-edu, blob-zh-edu, blob-en-work, blob-zh-work
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

# Value pools

SCHOOLS_EN = [
    "Stanford University", "MIT", "Harvard University", "University of Cambridge",
    "ETH Zurich", "Carnegie Mellon University", "University of Oxford",
    "University of Toronto", "Princeton University", "Yale University",
    "UC Berkeley", "UCLA", "NYU", "EPFL", "University of Edinburgh",
    "TU Munich", "National University of Singapore", "University of Sydney",
    "University of Melbourne", "Caltech", "Cornell University",
    "Columbia University", "University of Pennsylvania", "Duke University",
    "University of Chicago", "Imperial College London", "King's College London",
    "Johns Hopkins University", "University of Michigan", "Georgia Tech",
]

SCHOOLS_ZH = [
    "北京大学", "清华大学", "浙江大学", "复旦大学", "上海交通大学",
    "南京大学", "中国人民大学", "中国科学技术大学", "北京航空航天大学",
    "武汉大学", "同济大学", "厦门大学", "香港大学", "香港中文大学",
    "中山大学", "华中科技大学", "西安交通大学", "哈尔滨工业大学",
    "北京师范大学", "中国科学院大学", "南开大学", "天津大学",
    "山东大学", "四川大学", "重庆大学",
]

COMPANIES_EN = [
    "Google", "Meta", "Amazon", "Microsoft", "Apple", "NVIDIA", "OpenAI",
    "Anthropic", "Stripe", "Airbnb", "Uber", "Tesla", "Netflix", "Spotify",
    "Salesforce", "Databricks", "Snowflake", "Pinterest", "LinkedIn", "DoorDash",
    "Shopify", "Twitter", "Dropbox", "GitHub", "GitLab",
]

COMPANIES_ZH = [
    "字节跳动", "腾讯", "阿里巴巴", "百度", "美团", "京东", "滴滴",
    "网易", "华为", "小米", "拼多多", "快手", "B站", "Bilibili",
    "蚂蚁集团", "360", "新浪", "搜狐",
]

MAJORS_EN = [
    "Computer Science", "Electrical Engineering", "Mechanical Engineering",
    "Mathematics", "Statistics", "Physics", "Chemistry", "Biology",
    "Economics", "Finance", "Data Science", "Computer Vision",
    "Machine Learning", "Software Engineering", "Civil Engineering",
    "Industrial Engineering", "Materials Science", "Aerospace Engineering",
    "Bioinformatics", "Operations Research",
]

MAJORS_ZH = [
    "计算机科学与技术", "软件工程", "电子工程", "机械工程", "数学",
    "统计学", "物理学", "化学", "生物学", "经济学", "金融学",
    "计算机视觉", "人工智能", "数据科学", "控制工程", "土木工程",
    "材料科学", "航空航天工程", "生物信息学", "运筹学",
]

TITLES_EN = [
    "Software Engineer", "Senior Software Engineer", "Machine Learning Engineer",
    "Data Scientist", "Product Manager", "Research Scientist",
    "Research Engineer", "Principal Engineer", "Backend Developer",
    "Frontend Engineer", "Solutions Architect", "Engineering Manager",
    "iOS Developer", "Android Developer", "Site Reliability Engineer",
    "Data Engineer", "Quantitative Researcher", "Security Engineer",
]

TITLES_ZH = [
    "软件工程师", "高级工程师", "数据科学家", "产品经理", "算法工程师",
    "后端开发工程师", "前端工程师", "机器学习工程师", "研究员",
    "高级研究员", "工程经理", "解决方案架构师", "数据工程师",
    "运维工程师", "测试工程师",
]

TEAMS_EN = [
    "search infra", "recommendation systems", "ads platform", "payments",
    "growth", "core platform", "AWS", "Azure", "cloud services",
    "developer tools", "mobile platform", "search quality", "ML platform",
    "trust and safety", "data platform",
]

TEAMS_ZH = [
    "推荐系统", "广告平台", "搜索基础", "支付平台", "用户增长",
    "云服务", "开发者工具", "移动平台", "数据平台", "搜索质量",
    "信任与安全", "微信支付", "外卖业务", "搜索广告",
]

DEGREE_EN = {
    "Bachelor": ["BSc", "BS", "BA", "B.S.", "B.A.", "Bachelor", "Bachelor of Science",
                 "Bachelor of Arts", "Bachelor of Engineering", "BEng"],
    "Master":   ["MS", "MSc", "MA", "M.S.", "M.A.", "Master", "Master of Science",
                 "Master of Arts", "Master of Engineering", "MEng"],
    "PhD":      ["PhD", "Ph.D.", "Doctorate", "Doctor of Philosophy"],
}
DEGREE_ZH = {
    # `*在读` terms are intentionally omitted — they imply "still studying"
    # which conflicts with explicit date ranges in the same input.
    "Bachelor": ["学士", "学士学位", "本科", "本科学历"],
    "Master":   ["硕士", "硕士学位", "研究生", "硕士学历"],
    "PhD":      ["博士", "博士学位", "博士研究生"],
}

MONTH_NAMES_EN = {
    1: ["January", "Jan"], 2: ["February", "Feb"], 3: ["March", "Mar"],
    4: ["April", "Apr"], 5: ["May", "May"], 6: ["June", "Jun"],
    7: ["July", "Jul"], 8: ["August", "Aug"], 9: ["September", "Sept", "Sep"],
    10: ["October", "Oct"], 11: ["November", "Nov"], 12: ["December", "Dec"],
}

PRESENT_EN = ["present", "now", "current", "today"]
PRESENT_ZH = ["至今", "今", "现在"]


def yyyy_mm(year: int, month: int) -> str:
    return f"{year}-{month:02d}"


def fmt_date_en_full(year: int, month: int) -> str:
    """e.g. 'September 2018' or 'Sep 2018'."""
    name = random.choice(MONTH_NAMES_EN[month])
    return f"{name} {year}"


def fmt_date_zh(year: int, month: int) -> str:
    return f"{year}年{month}月"


def gen_year_range(*, allow_present: float = 0.1) -> Tuple[int, int, bool]:
    """Return (from_year, to_year, is_present). If is_present, to_year is ignored."""
    if random.random() < allow_present:
        return random.randint(2018, 2024), 0, True
    span = random.randint(2, 5)
    from_year = random.randint(2005, 2020)
    return from_year, min(from_year + span, 2024), False


# Each natural-language generator picks a date precision FIRST, then a template
# from the bucket compatible with that precision. Ground truth is computed from
# the same precision. This guarantees input text and ground truth never disagree
# about whether a month was specified.


def gen_nl_en_edu() -> Tuple[str, Dict[str, Any]]:
    school = random.choice(SCHOOLS_EN)
    major = random.choice(MAJORS_EN)
    label, phrases = random.choice(list(DEGREE_EN.items()))
    degree_phrase = random.choice(phrases)
    is_present = random.random() < (0.15 if label == "PhD" else 0.04)
    precision = random.choice(["year", "month"])

    if is_present:
        from_y = random.randint(2018, 2024)
        if precision == "month":
            from_m = random.randint(1, 12)
            from_d = yyyy_mm(from_y, from_m)
            from_text = fmt_date_en_full(from_y, from_m)
        else:
            from_d = str(from_y)
            from_text = str(from_y)
        to_d = "present"
        templates = [
            f"She is currently pursuing her {degree_phrase} in {major} at {school}, which she began in {from_text}.",
            f"Since {from_text}, I have been pursuing a {degree_phrase} in {major} at {school}.",
            f"He has been studying {major} at {school} since {from_text}, working towards a {degree_phrase}.",
        ]
    else:
        from_y, to_y, _ = gen_year_range(allow_present=0.0)
        if precision == "month":
            from_m = random.randint(1, 12)
            to_m = random.randint(1, 12)
            from_d, to_d = yyyy_mm(from_y, from_m), yyyy_mm(to_y, to_m)
            from_text = fmt_date_en_full(from_y, from_m)
            to_text = fmt_date_en_full(to_y, to_m)
            templates = [
                f"From {from_text} to {to_text}, I attended {school} where I studied {major} and earned my {degree_phrase}.",
                f"I graduated from {school} in {to_text} with a {degree_phrase} in {major}, having started in {from_text}.",
                f"She studied {major} at {school} from {from_text} to {to_text}, completing a {degree_phrase}.",
            ]
        else:
            from_d, to_d = str(from_y), str(to_y)
            templates = [
                f"Between {from_y} and {to_y} I studied {major} at {school}, completing a {degree_phrase}.",
                f"He spent several years at {school}, from {from_y} to {to_y}, earning a {degree_phrase} in {major}.",
                f"From {from_y} to {to_y} she attended {school} and earned a {degree_phrase} in {major}.",
            ]

    sentence = random.choice(templates)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": school,
        "major": major,
        "scholar": label,
        "is_work_experience": False,
    }
    return sentence, expected


def gen_nl_zh_edu() -> Tuple[str, Dict[str, Any]]:
    school = random.choice(SCHOOLS_ZH)
    major = random.choice(MAJORS_ZH)
    label, phrases = random.choice(list(DEGREE_ZH.items()))
    degree_phrase = random.choice(phrases)
    is_present = random.random() < (0.15 if label == "PhD" else 0.04)
    precision = random.choice(["year", "month"])

    if is_present:
        from_y = random.randint(2018, 2024)
        if precision == "month":
            from_m = random.randint(1, 12)
            from_d = yyyy_mm(from_y, from_m)
            from_text = fmt_date_zh(from_y, from_m)
        else:
            from_d = str(from_y)
            from_text = f"{from_y}年"
        to_d = "present"
        templates = [
            f"目前在{school}读{degree_phrase}，研究方向是{major}，{from_text}入学，至今仍在学。",
            f"她从{from_text}起在{school}攻读{degree_phrase}，专业是{major}，目前在读。",
            f"我自{from_text}起就读于{school}，主修{major}，{degree_phrase}在读。",
        ]
    else:
        from_y, to_y, _ = gen_year_range(allow_present=0.0)
        if precision == "month":
            from_m = random.randint(1, 12)
            to_m = random.randint(1, 12)
            from_d, to_d = yyyy_mm(from_y, from_m), yyyy_mm(to_y, to_m)
            from_text = fmt_date_zh(from_y, from_m)
            to_text = fmt_date_zh(to_y, to_m)
            templates = [
                f"我于{from_text}至{to_text}就读于{school}，主修{major}，获得{degree_phrase}。",
                f"她是{school}{major}专业的学生，攻读时间是{from_text}到{to_text}，取得{degree_phrase}。",
                f"他在{school}主修{major}，时间是从{from_text}到{to_text}，最终获得{degree_phrase}。",
            ]
        else:
            from_d, to_d = str(from_y), str(to_y)
            templates = [
                f"{from_y}年至{to_y}年，我在{school}攻读{major}专业，取得{degree_phrase}。",
                f"他于{from_y}至{to_y}年在{school}读{major}，获得{degree_phrase}。",
                f"我在{school}读了几年{major}，时间是{from_y}-{to_y}，毕业获得{degree_phrase}。",
            ]

    sentence = random.choice(templates)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": school,
        "major": major,
        "scholar": label,
        "is_work_experience": False,
    }
    return sentence, expected


def gen_nl_en_work() -> Tuple[str, Dict[str, Any]]:
    company = random.choice(COMPANIES_EN)
    title = random.choice(TITLES_EN)
    team = random.choice(TEAMS_EN)
    is_present = random.random() < 0.35
    precision = random.choice(["year", "month"])

    if is_present:
        from_y = random.randint(2017, 2024)
        if precision == "month":
            from_m = random.randint(1, 12)
            from_d = yyyy_mm(from_y, from_m)
            from_text = fmt_date_en_full(from_y, from_m)
        else:
            from_d = str(from_y)
            from_text = str(from_y)
        to_d = "present"
        templates = [
            f"I have been working at {company} as a {title} on the {team} team since {from_text}.",
            f"Since {from_text}, I have been a {title} at {company} working on the {team} team.",
            f"He joined {company} as a {title} in {from_text} and is still on the {team} team today.",
        ]
    else:
        from_y, to_y, _ = gen_year_range(allow_present=0.0)
        if precision == "month":
            from_m = random.randint(1, 12)
            to_m = random.randint(1, 12)
            from_d, to_d = yyyy_mm(from_y, from_m), yyyy_mm(to_y, to_m)
            from_text = fmt_date_en_full(from_y, from_m)
            to_text = fmt_date_en_full(to_y, to_m)
            templates = [
                f"From {from_text} to {to_text}, I worked at {company} as a {title} focusing on {team}.",
                f"She joined {company} as a {title} in {from_text} and left in {to_text} after working on the {team} team.",
                f"Between {from_text} and {to_text}, he was a {title} at {company} on the {team} team.",
            ]
        else:
            from_d, to_d = str(from_y), str(to_y)
            templates = [
                f"Between {from_y} and {to_y} she served as a {title} at {company}, primarily on the {team} team.",
                f"From {from_y} to {to_y} he was a {title} at {company} working on the {team} team.",
                f"He spent several years at {company}, from {from_y} to {to_y}, eventually rising to {title}.",
            ]

    sentence = random.choice(templates)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": company,
        "major": title,
        "scholar": None,
        "is_work_experience": True,
    }
    return sentence, expected


def gen_nl_zh_work() -> Tuple[str, Dict[str, Any]]:
    company = random.choice(COMPANIES_ZH)
    title = random.choice(TITLES_ZH)
    team = random.choice(TEAMS_ZH)
    is_present = random.random() < 0.35
    precision = random.choice(["year", "month"])

    if is_present:
        from_y = random.randint(2017, 2024)
        if precision == "month":
            from_m = random.randint(1, 12)
            from_d = yyyy_mm(from_y, from_m)
            from_text = fmt_date_zh(from_y, from_m)
        else:
            from_d = str(from_y)
            from_text = f"{from_y}年"
        to_d = "present"
        templates = [
            # Always include an explicit 至今 / 目前 marker so the input
            # unambiguously means "still there".
            f"{from_text}起，我加入{company}担任{title}至今，主要负责{team}。",
            f"我自{from_text}起在{company}担任{title}，目前仍在该岗位，负责{team}。",
            f"他从{from_text}起在{company}做{title}，至今未离职，方向是{team}。",
        ]
    else:
        from_y, to_y, _ = gen_year_range(allow_present=0.0)
        if precision == "month":
            from_m = random.randint(1, 12)
            to_m = random.randint(1, 12)
            from_d, to_d = yyyy_mm(from_y, from_m), yyyy_mm(to_y, to_m)
            from_text = fmt_date_zh(from_y, from_m)
            to_text = fmt_date_zh(to_y, to_m)
            templates = [
                f"从{from_text}到{to_text}，我在{company}任职{title}，负责{team}。",
                f"她在{company}担任{title}的时间是{from_text}至{to_text}，参与了{team}团队的工作。",
                f"{from_text}到{to_text}期间，我在{company}担任{title}，主要做{team}。",
            ]
        else:
            from_d, to_d = str(from_y), str(to_y)
            templates = [
                f"{from_y}至{to_y}年，他在{company}做{title}，团队是{team}。",
                f"我在{company}担任{title}的时间是{from_y}到{to_y}年，负责{team}。",
                f"{from_y}年至{to_y}年，我在{company}任职{title}，所在团队是{team}。",
            ]

    sentence = random.choice(templates)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": company,
        "major": title,
        "scholar": None,
        "is_work_experience": True,
    }
    return sentence, expected


# Blob formats

def gen_blob_en_edu() -> Tuple[str, Dict[str, Any]]:
    school = random.choice(SCHOOLS_EN)
    major = random.choice(MAJORS_EN)
    label, phrases = random.choice(list(DEGREE_EN.items()))
    degree = random.choice(phrases)
    from_y, to_y, is_present = gen_year_range(allow_present=0.1)
    from_m = random.randint(1, 12)
    to_m = random.randint(1, 12)
    use_months = random.random() < 0.5

    from_d = yyyy_mm(from_y, from_m) if use_months else str(from_y)
    to_d = "present" if is_present else (yyyy_mm(to_y, to_m) if use_months else str(to_y))

    # Use raw forms in the blob (not the normalized YYYY-MM) to make extraction nontrivial
    from_raw = f"{from_y}/{from_m}" if use_months else str(from_y)
    to_raw = "present" if is_present else (f"{to_y}/{to_m}" if use_months else str(to_y))

    templates = [
        f"name:?|degree:{degree}|school:{school}|major:{major}|time:{from_raw}-{to_raw}",
        f"Edu//{school}//{major}//{degree}//{from_raw}-{to_raw}",
        f"[education] school={school} major={major} degree={degree} from={from_raw} to={to_raw}",
        f"EDU>>>{school}|{major}|{degree}|{from_raw}-{to_raw}",
        f"school::{school};;major::{major};;degree::{degree};;time::{from_raw}-{to_raw}",
        f"<<edu>> {school} >> {major} >> {degree} >> {from_raw}-{to_raw}",
    ]
    sentence = random.choice(templates)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": school,
        "major": major,
        "scholar": label,
        "is_work_experience": False,
    }
    return sentence, expected


def gen_blob_zh_edu() -> Tuple[str, Dict[str, Any]]:
    school = random.choice(SCHOOLS_ZH)
    major = random.choice(MAJORS_ZH)
    label, phrases = random.choice(list(DEGREE_ZH.items()))
    degree = random.choice(phrases)
    from_y, to_y, is_present = gen_year_range(allow_present=0.1)
    from_m = random.randint(1, 12)
    to_m = random.randint(1, 12)
    use_months = random.random() < 0.5

    from_d = yyyy_mm(from_y, from_m) if use_months else str(from_y)
    to_d = "present" if is_present else (yyyy_mm(to_y, to_m) if use_months else str(to_y))

    from_raw = f"{from_y}.{from_m}" if use_months else str(from_y)
    to_raw = "至今" if is_present else (f"{to_y}.{to_m}" if use_months else str(to_y))

    templates = [
        f"学校:{school};专业:{major};学历:{degree};时间:{from_raw}-{to_raw}",
        f"[教育] {school}||{major}||{degree}||{from_raw}-{to_raw}",
        f"edu/{school}/{major}/{degree}/{from_raw}-{to_raw}",
        f"教育经历＞＞{school}＞＞{major}＞＞{from_raw}-{to_raw}＞＞{degree}",
        f"学校：{school}／专业：{major}／学位：{degree}／时间：{from_raw}-{to_raw}",
    ]
    sentence = random.choice(templates)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": school,
        "major": major,
        "scholar": label,
        "is_work_experience": False,
    }
    return sentence, expected


def gen_blob_en_work() -> Tuple[str, Dict[str, Any]]:
    company = random.choice(COMPANIES_EN)
    title = random.choice(TITLES_EN)
    team = random.choice(TEAMS_EN)
    from_y, to_y, is_present = gen_year_range(allow_present=0.4)
    from_m = random.randint(1, 12)
    to_m = random.randint(1, 12)

    from_d = yyyy_mm(from_y, from_m)
    to_d = "present" if is_present else yyyy_mm(to_y, to_m)
    from_raw = f"{from_y}.{from_m}"
    to_raw = "present" if is_present else f"{to_y}.{to_m}"

    templates = [
        f"job#1|{company}|{title}|{from_y}/{from_m}-{to_raw if is_present else str(to_y)+'/'+str(to_m)}|{team}",
        f"WORK[{company}][{from_y}-{to_y if not is_present else 'present'}][{title}][{team}]",
        f"[work] company={company} role={title} from={from_d} to={to_d} team={team}",
        f"career::{company}||{title}||{from_y}-{to_y if not is_present else 'present'}||{team}",
        f"{company}/{title}/{from_raw}-{to_raw}/{team}",
        f"exp|{company}|{title}|{from_raw}-{to_raw}|{team}",
    ]
    sentence = random.choice(templates)
    # When only year-level is shown in the blob, expected falls back to year-only
    if any(p in sentence for p in [f"[{from_y}-", f"::{from_y}-", f"||{from_y}-"]):
        from_d = str(from_y)
        to_d = "present" if is_present else str(to_y)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": company,
        "major": title,
        "scholar": None,
        "is_work_experience": True,
    }
    return sentence, expected


def gen_blob_zh_work() -> Tuple[str, Dict[str, Any]]:
    company = random.choice(COMPANIES_ZH)
    title = random.choice(TITLES_ZH)
    team = random.choice(TEAMS_ZH)
    from_y, to_y, is_present = gen_year_range(allow_present=0.4)
    from_m = random.randint(1, 12)
    to_m = random.randint(1, 12)

    from_d = yyyy_mm(from_y, from_m)
    to_d = "present" if is_present else yyyy_mm(to_y, to_m)
    from_raw = f"{from_y}.{from_m}"
    to_raw = "至今" if is_present else f"{to_y}.{to_m}"

    templates = [
        f"工作｜{from_raw}-{to_raw}｜{company}｜{title}｜{team}",
        f"公司:{company} 职位:{title} 时间:{from_raw}-{to_raw} 部门:{team}",
        f"[work] {company}::{title}::{from_y}-{to_y if not is_present else '至今'}::{team}",
        f"career→{company}→{title}→{from_raw}-{to_raw}→{team}",
        f"工作经历＞＞{company}＞＞{title}＞＞{from_y}-{to_y if not is_present else '至今'}＞＞{team}",
    ]
    sentence = random.choice(templates)
    if any(p in sentence for p in [f"::{from_y}-", f"＞＞{from_y}-"]):
        from_d = str(from_y)
        to_d = "present" if is_present else str(to_y)
    expected = {
        "from": from_d,
        "to": to_d,
        "school": company,
        "major": title,
        "scholar": None,
        "is_work_experience": True,
    }
    return sentence, expected


# Messy overlays apply random surface noise without changing the ground truth.
# These exist to stress the extractor on real-world surface inconsistency:
# typos, missing punctuation, ALL-CAPS, abbreviations, etc.

def _messy_typo(s: str) -> str:
    """Drop one inner character or swap two adjacent ones."""
    if len(s) < 4:
        return s
    i = random.randint(1, len(s) - 2)
    if random.random() < 0.5:
        return s[:i] + s[i + 1:]
    return s[:i] + s[i + 1] + s[i] + s[i + 2:]


def _messy_school(school: str) -> str:
    op = random.choice(["lower", "upper", "no_space", "typo", "verbatim"])
    if op == "lower":
        return school.lower()
    if op == "upper":
        return school.upper()
    if op == "no_space":
        return school.replace(" ", "")
    if op == "typo":
        return _messy_typo(school)
    return school


def gen_messy_en_edu() -> Tuple[str, Dict[str, Any]]:
    """Row with surface-noisy formatting but extractable content (EN edu)."""
    school = random.choice(SCHOOLS_EN)
    major = random.choice(MAJORS_EN)
    label, phrases = random.choice(list(DEGREE_EN.items()))
    degree = random.choice(phrases)
    from_y = random.randint(2008, 2020)
    to_y = min(from_y + random.randint(2, 5), 2024)
    school_disp = _messy_school(school)
    from_yy = str(from_y)[2:]
    to_yy = str(to_y)[2:]
    templates = [
        f"{school_disp}, {major}, {degree}, {from_y}-{to_y}",
        f"{from_y}-{to_y}  {school_disp}  {major}  {degree}",
        f"'{from_yy}-'{to_yy} {school_disp} {major} {degree}",
        f"{school_disp.upper()} / {major.lower()} / {degree} / {from_y}-{to_y}",
    ]
    sentence = random.choice(templates)
    expected = {
        "from": str(from_y),
        "to": str(to_y),
        "school": school,
        "major": major,
        "scholar": label,
        "is_work_experience": False,
        "status": "success",
    }
    return sentence, expected


# Archive cases: inputs that are NOT extractable records and should be
# routed to the archive bucket by the LLM.

_ARCHIVE_GARBAGE = [
    "",
    "   ",
    "?",
    "...",
    "---",
    "***",
    "n/a",
    "N/A",
    "TBD",
    "TBC",
    "123",
    "0000",
    "asdfgh",
    "qwerty",
    "lorem ipsum dolor sit amet",
    "今天天气真好",
    "hello world",
    "你好世界",
    "&lt;empty&gt;",
    "[ERROR] connection refused at 03:42:11",
    "NULL",
    "null",
    "undefined",
    "无",
    "暂无",
    "—",
    "—————",
    "💀💀💀",
    "data_loss",
    "(see attached)",
    "见附件",
    "see resume",
    "no info",
    "缺失",
    "[redacted]",
    "##########",
    "<no record>",
    "===",
    ":-)",
]


def gen_archive_case() -> Tuple[str, Dict[str, Any]]:
    text = random.choice(_ARCHIVE_GARBAGE)
    expected = {
        "from": None,
        "to": None,
        "school": None,
        "major": None,
        "scholar": None,
        "is_work_experience": None,
        "status": "archived",
    }
    return text, expected


# Mark all "normal" generators as producing success rows.

def _wrap_success(gen):
    def _w():
        text, exp = gen()
        exp = dict(exp)
        exp["status"] = "success"
        return text, exp
    return _w


GENERATORS: List[Tuple[str, Callable[[], Tuple[str, Dict[str, Any]]]]] = [
    ("nl-en-edu", _wrap_success(gen_nl_en_edu)),
    ("nl-zh-edu", _wrap_success(gen_nl_zh_edu)),
    ("nl-en-work", _wrap_success(gen_nl_en_work)),
    ("nl-zh-work", _wrap_success(gen_nl_zh_work)),
    ("blob-en-edu", _wrap_success(gen_blob_en_edu)),
    ("blob-zh-edu", _wrap_success(gen_blob_zh_edu)),
    ("blob-en-work", _wrap_success(gen_blob_en_work)),
    ("blob-zh-work", _wrap_success(gen_blob_zh_work)),
    ("messy-en-edu", gen_messy_en_edu),
    ("archive", gen_archive_case),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="evaluation/eval_dataset_1000.json")
    args = parser.parse_args()

    random.seed(args.seed)

    rows: List[Dict[str, Any]] = []
    for i in range(args.n):
        category, gen = random.choice(GENERATORS)
        text, expected = gen()
        rows.append({
            "id": i + 1,
            "category": category,
            "input": text,
            "expected": expected,
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {out}")
    print("Category distribution:")
    from collections import Counter
    for cat, n in Counter(r["category"] for r in rows).most_common():
        print(f"  {cat:<14} {n}")


if __name__ == "__main__":
    main()
