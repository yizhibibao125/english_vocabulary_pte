#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTE 题目中文翻译脚本 (Windows)
================================
使用方法：
  1. 安装依赖（确保已开启 VPN）：
       pip install deep-translator
  2. 运行脚本：
       python translate_all.py
  3. 翻译完成后把生成的 data.json 上传到 GitHub 对应文件夹替换旧文件

说明：
  - 自动识别每个题型 JSON 中没有中文翻译的字段
  - 翻译结果直接写回 JSON 文件
  - 已有翻译的条目不会重复翻译
  - 如果翻译失败会跳过并打印错误，不影响其他条目
"""

import json, os, time, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 需要翻译的题型和对应字段（仅6个）
TASKS = [
    # RA 不需要翻译（逐句翻译已在文档中）

    # RTS: 情景和参考答案需要中文翻译
    ("RTS(respond to situation)题目列表 - 155题",
     "data.json", ["situation", "answer"]),

    # SWT: 文章和参考答案需要中文翻译
    ("SWT(summarize written text)题目列表 - 216题",
     "data.json", ["question", "answer"]),

    # SST: 参考答案需要中文翻译
    ("SST(summarize spoken text)题目列表 - 294题",
     "data.json", ["answer"]),

    # RL: 参考答案需要中文翻译
    ("RL(retell lecture)题目列表 - 242题",
     "data.json", ["answer"]),

    # DI: 参考答案需要中文翻译
    ("DI(describe image)题目列表 - 464题",
     "data.json", ["answer"]),
]

def is_chinese(text):
    """检查文本是否已包含中文"""
    return any('\u4e00' <= c <= '\u9fff' for c in str(text or ''))

def translate_text(translator, text):
    """翻译单条文本，失败返回空字符串"""
    text = str(text or '').strip()
    if not text or len(text) < 2:
        return ''
    # 超长文本截断（Google 限制5000字符）
    if len(text) > 4500:
        text = text[:4500]
    try:
        result = translator.translate(text)
        return result if result else ''
    except Exception as e:
        print(f"    翻译失败: {str(e)[:60]}")
        return ''

def process_file(translator, folder, json_file, fields):
    path = os.path.join(BASE_DIR, folder, json_file)
    if not os.path.exists(path):
        print(f"  ⚠️  文件不存在: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total = len(data)
    changed = 0

    for i, item in enumerate(data):
        for field in fields:
            en_val = item.get(field, '')
            zh_field = field.replace('_en', '_zh') if '_en' in field else field + '_zh'

            # 已有中文翻译则跳过
            if item.get(zh_field) and is_chinese(item.get(zh_field, '')):
                continue
            # 原文为空则跳过
            if not en_val or not str(en_val).strip():
                continue
            # 原文本身是中文则跳过
            if is_chinese(en_val):
                continue

            zh = translate_text(translator, en_val)
            if zh:
                item[zh_field] = zh
                changed += 1

        # 进度显示
        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"  进度: {i+1}/{total} (已翻译 {changed} 条)", end='\r')

        # 每翻译50条暂停0.5秒，避免触发限流
        if changed > 0 and changed % 50 == 0:
            time.sleep(0.5)

    print(f"  完成: {total} 条，新增翻译 {changed} 条          ")

    # 保存
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

def main():
    # 检查 deep-translator
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("❌ 未安装 deep-translator，请先运行：")
        print("   pip install deep-translator")
        sys.exit(1)

    translator = GoogleTranslator(source='en', target='zh-CN')

    # 测试连接
    print("🔗 测试 Google 翻译连接...")
    try:
        test = translator.translate("hello")
        print(f"✅ 连接成功！测试翻译: hello → {test}\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("   请确认 VPN 已开启，然后重试。")
        sys.exit(1)

    print(f"📋 共 {len(TASKS)} 个题型需要处理\n")

    for idx, (folder, json_file, fields) in enumerate(TASKS, 1):
        code = folder.split('(')[0] if '(' in folder else folder[:10]
        print(f"[{idx}/{len(TASKS)}] {code} ...", end=' ')
        sys.stdout.flush()
        try:
            process_file(translator, folder, json_file, fields)
        except KeyboardInterrupt:
            print("\n\n⛔ 用户中断，已保存当前进度")
            sys.exit(0)
        except Exception as e:
            print(f"\n  ❌ 错误: {e}")
            continue

    print("\n🎉 全部完成！")
    print("\n接下来：")
    print("  把各题型文件夹里的 data.json 上传到 GitHub 替换旧文件")
    print("  网站会自动显示中文翻译，无需修改 HTML")

if __name__ == '__main__':
    main()
