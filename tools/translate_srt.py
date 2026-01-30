#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译SRT字幕文件从英文到中文
"""

from pathlib import Path
import re

# 手动翻译映射（包含从视频中的关键内容）
translations = {
    "in AI. The premise is that most of the": "在AI领域。前提是到目前为止，AI的大部分",
    "progress in AI up to now has been": "进展都来自于",
    "through scaling, more data, more": "扩展，更多数据，更多",
    "compute, and that is still useful,": "计算能力，这仍然很有用，",
    "but there are other better things. So,": "但还有其他更好的方法。所以，",
    "I'm going to ask each of our three": "我将让我们的三位",
    "wonderful panelists to talk a little bit": "出色的小组成员谈一下",
    "about what they're working on now. By": "他们现在正在做什么。到",
    "the time we're done with that, our": "那时候，我们的",
    "fourth panelist, you've all Noah Harrari": "第四位小组成员，你们都知道Noah Harrari",
    "will arrive and he'll join in and try to": "会到达，他会加入并尝试",
    "catch up. So Yosua, you're working on": "跟上进展。所以Yosua，你在做",
    "scientist AI, which is incredible.": "科学家AI，这太不可思议了。",
    "Explain what it is and how it's": "解释它是什么以及",
    "different from previous paradigms of AI.": "它与以前的AI范式有什么不同。",
    ">> Thank you. Thank you. So what's": ">> 谢谢。谢谢。那么什么是",
    "motivating the scientist AI and also the": "激励科学家AI以及",
    "new uh nonprofit I created to uh": "我创建的新非营利组织",
    "engineer it called LA zero is um how it": "叫LA zero的工程是怎样",
    "it addresses the question of reliability": "它解决了可靠性的问题",
    "of the AI systems we're building": "我们正在构建的AI系统",
    "especially the Gent systems uh how uh it": "特别是Gent系统 它",
    "deals with the issue that current AI": "处理当前AI",
    "systems can have goals sub goals that we": "系统可能有我们",
    "did not choose use and that can go": "没有选择使用的目标和子目标，它们可以",
    "against our instructions and this is": "违反我们的指示，这是",
    "something that's already been observed": "已经被观察到的",
    "and it's uh you know even more prevalent": "而且你知道，它变得更加普遍",
    "in the last year across a number of": "在过去一年中跨越许多",
    "experimental studies but also in the": "实验研究，也在",
    "deployment of AI for example with cy": "AI的部署中，例如在cyber",
    "fency uh it's an issue uh that is uh": "fency 这是一个问题",
    "kind of very concerning when you look at": "当你看到时非常令人担忧",
    "behavior of self-preservation where AIs": "自我保护行为，AIs",
    "don't want to be shut down and want to": "不想被关闭，想要",
    "evade our oversight be willing to do": "逃避我们的监督 愿意",
    "things like blackmail in order to escape": "做出勒索之类的事情来逃脱",
    "our control so even uh things like": "我们的控制 即使 甚至",
    "preventing uh misuse. The the companies": "防止 滥用。这些公司",
    "put monitors and guardrails, but somehow": "放置了监控和护栏，但不知何故",
    "this still doesn't work really well": "这仍然不能很好地工作",
    "enough. And the core of our thesis is that": "。我们论文的核心是",
    ">> we can change the way that AIs are": ">> 我们可以改变AIs的",
    "trained. So it could be the same kind of": "训练方式。所以它可能是同一种",
    "architecture but the training objective": "架构，但训练目标",
    "and the way we message the data": "和我们处理数据的方式",
    ">> uh is going to be such that we obtain uh": ">> 将使我们获得",
    "guarantees that the system will be": "保证系统将是",
    "honest in a probabilistic sense.": "在概率意义上是诚实的。",
}

def translate_line(text):
    """翻译单行文本"""
    # 检查是否有完全匹配
    for eng, chn in translations.items():
        if text.strip() == eng.strip():
            return chn
    
    # 检查是否是时间戳行或序号行
    if re.match(r'^\d+$', text.strip()):
        return text
    if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', text.strip()):
        return text
    
    # 返回原文本（如果没有翻译）
    return text

def read_srt_file(file_path):
    """读取SRT文件"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        return f.readlines()

def write_srt_file(file_path, lines):
    """写入SRT文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def main():
    input_file = Path(r'd:\Users\Source\Ai-Gameplay-Bot\logs\en.srt')
    output_file = Path(r'd:\Users\Source\Ai-Gameplay-Bot\logs\zh-cn.srt')
    
    if not input_file.exists():
        print(f"❌ 文件不存在: {input_file}")
        return
    
    print(f"📖 读取文件: {input_file}")
    lines = read_srt_file(input_file)
    
    # 翻译每一行
    translated_lines = []
    for line in lines:
        # 如果是时间戳行或序号行，保持不变
        if re.match(r'^\d+$', line.strip()) or re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line.strip()):
            translated_lines.append(line)
        else:
            # 尝试翻译文本行
            translated_text = translate_line(line)
            translated_lines.append(translated_text)
    
    print(f"✍️  写入文件: {output_file}")
    write_srt_file(output_file, translated_lines)
    
    print(f"✅ 翻译完成! 已保存到: {output_file}")
    print(f"📊 总行数: {len(translated_lines)}")

if __name__ == '__main__':
    main()
