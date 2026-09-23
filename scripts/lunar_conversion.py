#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""农历 → 公历换算脚本（支持 1900-2100，含闰月）。

用法:
    python3 lunar_conversion.py <lunar_year> <lunar_month> <lunar_day> [--leap]

示例:
    python3 lunar_conversion.py 2026 8 15          # 2026年八月十五
    python3 lunar_conversion.py 2025 4 15 --leap   # 2025年闰四月十五

执行策略（按可靠性优先）:
    1. 依次尝试已安装的农历库: lunardate / sxtwl / lunar_python
    2. 全部不可用时，输出明确提示，由 AI 走「万年历检索」兜底路径
       （见 references/lunar-conversion.md），返回退出码 2。
"""
import sys


class InvalidLunarInput(ValueError):
    """输入的农历年月日在该年不存在（含无此闰月）。"""


def try_lunardate(year, month, day, leap):
    """优先库: lunardate (pip install lunardate)"""
    try:
        from lunardate import LunarDate
    except ImportError:
        return None
    try:
        d = LunarDate(year, month, day, isLeapMonth=leap).toSolarDate()
    except ValueError as exc:
        raise InvalidLunarInput(
            f"{year}年不存在「{'闰' if leap else ''}{month}月{day}日」，请核对农历月份与是否闰月。"
        ) from exc
    return d


def try_lunar_python(year, month, day, leap):
    """候选库: lunar_python (pip install lunar_python)"""
    try:
        from lunar_python import Lunar
    except ImportError:
        return None
    solar = Lunar.fromYmd(year, month, day).getSolar()
    return solar


def try_sxtwl(year, month, day, leap):
    """候选库: sxtwl (pip install sxtwl)"""
    try:
        import sxtwl
    except ImportError:
        return None
    day_ = sxtwl.fromLunar(year, month, day, leap)
    return day_.getSolarYear(), day_.getSolarMonth(), day_.getSolarDay()


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
    except ValueError:
        print("参数必须为整数: <lunar_year> <lunar_month> <lunar_day>")
        return 1

    leap = "--leap" in sys.argv[2:]

    if not (1900 <= year <= 2100):
        print(f"年份 {year} 超出 1900-2100 支持范围，无法可靠换算，请改用万年历人工核对。")
        return 2

    try:
        result = try_lunardate(year, month, day, leap)
        if result is None:
            result = try_lunar_python(year, month, day, leap)
        if result is None:
            result = try_sxtwl(year, month, day, leap)
    except InvalidLunarInput as exc:
        print(str(exc))
        return 2
    except ValueError as exc:
        print(f"输入的农历日期无法换算：{exc}。请核对月份、日与闰月标记。")
        return 2

    if result is None:
        print(
            "当前环境无农历换算库（lunardate / sxtwl / lunar_python）。\n"
            "请改走万年历检索兜底路径：用通用搜索查询「{year}年农历{月}{日}是公历几月几日」"
            "（闰月加「闰」字），两个独立来源一致后采信。\n"
            "如环境可联网安装依赖，可执行: pip install lunardate"
        )
        return 2

    # 统一输出格式 YYYY-MM-DD
    if hasattr(result, "year"):  # lunardate / lunar_python 返回 date 对象
        print(result.strftime("%Y-%m-%d"))
    else:  # sxtwl 返回元组
        y, m, d = result
        print(f"{y:04d}-{m:02d}-{d:02d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
