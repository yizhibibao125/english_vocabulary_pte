#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门为 RL 和 SST 的音频内容（extra_text）添加中文翻译
运行方法：python fix_extra_text_zh.py
"""
import json, os, sys, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TASKS = [
    "SST(summarize spoken text)题目列表 - 294题",
    "RL(retell lecture)题目列表 - 242题",
]

def is_chinese(s):
    return any('\u4e00' <= c <= '\u9fff' for c in str(s or ''))

def main():
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        print("❌ 请先运行: pip install deep-translator")
        sys.exit(1)

    translator = GoogleTranslator(source='en', target='zh-CN')

    # 测试连接
    try:
        t = translator.translate("hello")
        print(f"✅ 连接成功: hello → {t}\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}\n请确认 VPN 已开启")
        sys.exit(1)

    for folder in TASKS:
        path = os.path.join(BASE_DIR, folder, 'data.json')
        print(f"处理: {folder[:40]}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        changed = 0
        for i, item in enumerate(data):
            # 只有当 extra_text_zh 有实际中文内容时才跳过
            existing = item.get('extra_text_zh', None)
            if existing and isinstance(existing, str) and len(existing) > 5 and is_chinese(existing):
                continue

            # 过滤 extra_text 里的标签行和中文行，合并成一段文字
            lines = item.get('extra_text', [])
            en_lines = [l for l in lines
                        if l and not is_chinese(l)
                        and l not in ('音频原文', '音频原文：')]
            if not en_lines:
                continue

            text = ' '.join(en_lines)
            if len(text) > 4500:
                text = text[:4500]

            try:
                zh = translator.translate(text)
                if zh:
                    item['extra_text_zh'] = zh
                    changed += 1
            except Exception as e:
                print(f"  第{i+1}条翻译失败: {str(e)[:50]}")

            # 每50条暂停一下
            if changed > 0 and changed % 50 == 0:
                time.sleep(0.5)

            # 进度
            if (i + 1) % 30 == 0 or (i + 1) == len(data):
                print(f"  进度: {i+1}/{len(data)}, 已翻译 {changed} 条", end='\r')

        print(f"  完成: 共翻译 {changed} 条            ")

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        print(f"  ✅ 已保存\n")

    print("🎉 全部完成！把 RL 和 SST 的 data.json 上传到 GitHub 即可。")

if __name__ == '__main__':
    main()
