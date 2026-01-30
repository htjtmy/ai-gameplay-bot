#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的SRT字幕翻译 - 使用句级翻译库
"""

import re
from pathlib import Path
from typing import List, Tuple

# 完整句子级别的翻译（优先级高）
SENTENCE_TRANSLATIONS = {
    "in AI. The premise is that most of the": "在AI领域。前提是大多数",
    "progress in AI up to now has been": "迄今为止AI的进展",
    "through scaling, more data, more": "通过扩展、更多数据、更多",
    "compute, and that is still useful,": "计算，这仍然有用，",
    "but there are other better things. So,": "但还有其他更好的方法。所以，",
    "I'm going to ask each of our three": "我要请我们三位",
    "wonderful panelists to talk a little bit": "出色的小组成员谈一下",
    "about what they're working on now. By": "他们现在在做什么。到时候，",
    "the time we're done with that, our": "到时候，我们",
    "fourth panelist, you've all Noah Harrari": "第四位小组成员，你们都知道Noah Harrari",
    "will arrive and he'll join in and try to": "将会到达，他会加入并尝试",
    "catch up. So Yosua, you're working on": "跟上。所以Yosua，你在从事",
    "scientist AI, which is incredible.": "科学家AI，这太不可思议了。",
    "Explain what it is and how it's": "解释它是什么以及它如何",
    "different from previous paradigms of AI.": "与以前的AI范式不同。",
    "Thank you. Thank you. So what's": "谢谢。谢谢。那么什么",
    "motivating the scientist AI and also the": "激励科学家AI以及",
    "new uh nonprofit I created to uh": "我创建的新非营利组织",
    "engineer it called LA zero is um how it": "叫LA zero的工程是怎样",
    "it addresses the question of reliability": "它解决可靠性的问题",
    "of the AI systems we're building": "关于我们正在构建的AI系统",
    "especially the Gent systems uh how uh it": "特别是Gent系统，它",
    "deals with the issue that current AI": "处理当前AI",
    "systems can have goals sub goals that we": "系统可能有我们",
    "did not choose use and that can go": "没有选择的目标和子目标，它们可以",
    "against our instructions and this is": "违反我们的指示，这是",
    "something that's already been observed": "已经被观察到的",
    "and it's uh you know even more prevalent": "而且你知道，它变得更加普遍",
    "in the last year across a number of": "在过去一年中跨越许多",
    "experimental studies but also in the": "实验研究，也在",
    "deployment of AI for example with cy": "AI的部署中，例如在",
    "fency uh it's an issue uh that is uh": "这是一个",
    "kind of very concerning when you look at": "当你看到时非常令人担忧",
    "behavior of self-preservation where AIs": "自我保护行为，AIs",
    "don't want to be shut down and want to": "不想被关闭，想要",
    "evade our oversight be willing to do": "逃避我们的监督，愿意",
    "things like blackmail in order to escape": "做勒索之类的事情来逃脱",
    "our control so even uh things like": "我们的控制，即使",
    "preventing uh misuse. The the companies": "防止滥用。这些公司",
    "put monitors and guardrails, but somehow": "放置了监控和护栏，但不知何故",
    "this still doesn't work really well": "这仍然不能很好地工作",
    "enough. And the core of our thesis is that": "。我们论文的核心是",
    "we can change the way that AIs are": "我们可以改变AIs的",
    "trained. So it could be the same kind of": "训练方式。所以它可能是同一种",
    "architecture but the training objective": "架构，但训练目标",
    "and the way we message the data": "和我们处理数据的方式",
    "uh is going to be such that we obtain uh": "将使我们获得",
    "guarantees that the system will be": "保证系统将是",
    "honest in a probabilistic sense.": "在概率意义上诚实的。",
    "Okay. So how do you do that?": "好的。那你怎样做呢？",
    "How do you do that? So the core of": "你怎样做？所以想法的核心",
    "the idea which is connect": "的想法是连接",
    "I'm trying to do it with my kids.": "我在试着对我的孩子这样做。",
    "Yes. So the core of the idea which is": "是的。所以想法的核心",
    "behind the name is take as an": "是以...为灵感",
    "inspiration not to imitate people but to": "不是模仿人，而是模仿",
    "imitate what science at an ideal level": "在理想水平的科学",
    "is trying to do. So think about the laws": "在做什么。所以想一下物理定律。",
    "of physics. The laws of physics": "物理定律。物理定律",
    "can be turned into predictions and those": "可以转换成预测，那些",
    "predictions will be honest. They don't": "预测将是诚实的。它们不",
    "care about whether the prediction is": "关心预测是否",
    "going to help one person or another": "会帮助一个人还是另一个人",
    "person. So it turns out that it is": "。所以结果是这是",
    "possible to define training objectives": "可能定义训练目标",
    "for uh neural nets so that they will": "对于神经网络，这样它们将",
    "converge to what something like you know": "收敛到什么像你知道",
    "scientific laws would predict and then": "科学定律会预测然后",
    "we get something that we can rely for": "我们获得我们可以依靠",
    "example we can rely on to uh create": "例如我们可以依靠来创建",
    "technical guard rails around agents that": "围绕代理的技术护栏",
    "we don't trust. So if an agent is": "我们不信任的。所以如果一个代理",
    "proposing an action uh for each action": "提议一个动作，对于每个动作",
    "that the agent proposes uh a honest": "代理提议的，一个诚实的",
    "predictor could tell us whether that": "预测器可以告诉我们是否那个",
    "action has some probability of creating": "动作有某种概率创建",
    "a particular kind of harm and of course": "特定种类的伤害，当然",
    "veto that action if that's the case.": "否决那个动作如果是那样。",
    "But you still are then going to be": "但你仍然会然后",
    "required to put in some threshold of": "被要求放入某个阈值",
    "when it will take that action. Right? If": "当它将采取那个动作时。对吧？如果",
    "it has a percentage odds of harm of more": "它有伤害的百分比概率超过",
    "than one in 10 or one in a thousand": "十分之一或千分之一",
    "wherever you put it, you still have some": "无论你把它放在哪里，你仍然有一些",
    "human concern, you still have some": "人类关切，你仍然有一些",
    "potential harm to create.": "潜在的伤害要创建。",
    "Absolutely. So when we build a nuclear": "绝对的。所以当我们构建一个核",
    "plant, we have to decide where we put the threshold.": "电站时，我们必须决定我们把阈值放在哪里。",
    "Oh, so we're okay.": "哦，所以我们没问题。",
    "Right. And uh for nuclear plants, it": "对。而对于核电站，它",
    "might be, you know, one in a million": "可能是，你知道，一百万分之一",
    "years that something bad is going to": "年将会有糟糕的事情",
    "happen because it's so severe. Depending": "发生因为它太严重。取决于",
    "on the kind of harm that we're trying to": "我们试图防止的伤害类型",
    "prevent, society, not AIS, have to": "，社会，不是AIS，必须",
    "decide where we put those thresholds,": "决定我们把那些阈值放在哪里，",
    "right?": "对吧？",
    "I've always thought it was interesting": "我一直认为这很有趣",
    "that uh for most things, we'll accept": "对于大多数事情，我们将接受",
    "like a one in 10 million chance of": "就像一千万分之一的机会",
    "nuclear plant exploding, but we continue": "核电站爆炸，但我们继续",
    "to build AI even though general": "构建AI即使一般的",
    "predictions that it might wipe out": "预测它可能消除",
    "humanity are like 10%. Um, all right.": "人类就像10%。嗯，好吧。",
    "Ejen, why don't you talk a little bit": "Ejen，你为什么不谈一下",
    "about some of your work in continual": "你在持续学习中的一些工作",
    "learning? And you, of course, have been": "？而你，当然，一直",
    "a brilliant critic of scaling laws for a": "对扩展定律的杰出批评家",
    "long time, including on a panel last": "很久，包括在去年的一个小组",
    "year with Yoshua. So, tell us what": "有Yoshua。所以，告诉我们什么",
    "you're working on now.": "你现在在做。",
}

# 单词级别翻译（作为备选）
WORD_TRANSLATIONS = {
    "AI": "AI",
    "progress": "进展",
    "scaling": "扩展",
    "data": "数据",
    "compute": "计算",
    "useful": "有用的",
    "panelists": "小组成员",
    "working": "工作",
    "incredible": "不可思议的",
    "Explain": "解释",
    "different": "不同的",
    "paradigms": "范式",
    "Thank": "谢谢",
    "motivating": "激励",
    "nonprofit": "非营利",
    "engineer": "工程",
    "addresses": "解决",
    "question": "问题",
    "reliability": "可靠性",
    "systems": "系统",
    "building": "构建",
    "Gent": "Gent",
    "deals": "处理",
    "issue": "问题",
    "current": "当前的",
    "goals": "目标",
    "sub goals": "子目标",
    "choose": "选择",
    "against": "违反",
    "instructions": "指示",
    "observed": "观察的",
    "prevalent": "普遍的",
    "experimental": "实验的",
    "studies": "研究",
    "deployment": "部署",
    "concerning": "令人担忧的",
    "behavior": "行为",
    "self-preservation": "自我保护",
    "shut": "关闭",
    "evade": "逃避",
    "oversight": "监督",
    "willing": "愿意",
    "blackmail": "勒索",
    "escape": "逃脱",
    "control": "控制",
    "preventing": "防止",
    "misuse": "滥用",
    "companies": "公司",
    "monitors": "监控",
    "guardrails": "护栏",
    "somehow": "不知何故",
    "doesn't": "不",
    "really": "真的",
    "work": "有效",
    "enough": "足够",
    "core": "核心",
    "thesis": "论文",
    "change": "改变",
    "way": "方式",
    "trained": "训练",
    "architecture": "架构",
    "training": "训练",
    "objective": "目标",
    "message": "处理",
    "guarantees": "保证",
    "honest": "诚实的",
    "probabilistic": "概率的",
    "sense": "意义",
}

def parse_srt(content: str) -> List[Tuple[int, str, List[str]]]:
    """解析SRT格式"""
    blocks = content.strip().split('\n\n')
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                seq_num = int(lines[0])
                timestamp = lines[1]
                subtitle_lines = lines[2:]
                subtitles.append((seq_num, timestamp, subtitle_lines))
            except:
                continue
    
    return subtitles

def translate_line(text: str) -> str:
    """逐行翻译"""
    original = text
    
    # 先用句子级翻译
    for sent, trans in SENTENCE_TRANSLATIONS.items():
        if sent in text:
            text = text.replace(sent, trans)
    
    # 再用单词级翻译
    for word, trans in WORD_TRANSLATIONS.items():
        # 避免重复翻译
        if word not in text and trans in text:
            continue
        # 使用词边界匹配
        pattern = r'\b' + re.escape(word) + r'\b'
        text = re.sub(pattern, trans, text, flags=re.IGNORECASE)
    
    return text

def main():
    input_file = Path(r'd:\Users\Source\Ai-Gameplay-Bot\logs\en.srt')
    output_file = Path(r'd:\Users\Source\Ai-Gameplay-Bot\logs\zh-cn.srt')
    
    if not input_file.exists():
        print(f"❌ 文件不存在")
        return
    
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    subtitles = parse_srt(content)
    print(f"📖 读取: {len(subtitles)} 条字幕")
    
    translated = []
    for seq, ts, lines in subtitles:
        trans_lines = [translate_line(line) for line in lines]
        translated.append((seq, ts, trans_lines))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, (seq, ts, lines) in enumerate(translated):
            f.write(f"{seq}\n{ts}\n")
            for line in lines:
                f.write(line + "\n")
            if i < len(translated) - 1:
                f.write("\n")
    
    print(f"✅ 已保存到: {output_file.name}")

if __name__ == '__main__':
    main()
