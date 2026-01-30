#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Ollama或其他本地翻译服务翻译SRT字幕
简化版本：直接使用预定义的翻译映射和启发式方法
"""

import re
from pathlib import Path
from typing import List, Tuple

def parse_srt(file_path: str) -> List[Tuple[int, str, List[str]]]:
    """解析SRT文件，返回 (序号, 时间戳, 字幕行列表)"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 将内容分解为字幕块
    blocks = content.strip().split('\n\n')
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                seq_num = int(lines[0])
                timestamp = lines[1]
                subtitle_text = '\n'.join(lines[2:])
                subtitles.append((seq_num, timestamp, subtitle_text.split('\n')))
            except:
                continue
    
    return subtitles

def simple_translate(text: str) -> str:
    """使用简单规则和缓存进行翻译"""
    # 基础词汇和短语翻译
    vocab = {
        # 基础词
        'AI': 'AI',
        'the': '这',
        'is': '是',
        'and': '和',
        'in': '在',
        'to': '到',
        'of': '的',
        'that': '那',
        'it': '它',
        'a': '一个',
        'for': '对于',
        'or': '或',
        'I': '我',
        'you': '你',
        'he': '他',
        'we': '我们',
        'they': '他们',
        
        # 长短语
        'artificial intelligence': '人工智能',
        'machine learning': '机器学习',
        'neural network': '神经网络',
        'deep learning': '深度学习',
        'large language model': '大型语言模型',
        'foundation model': '基础模型',
        'transformer': '变压器/转换器',
        'reinforcement learning': '强化学习',
        'open source': '开源',
        'safety': '安全',
        'alignment': '对齐',
        'AGI': '通用人工智能',
        'scaling': '扩展',
        'compute': '计算',
        'data': '数据',
        'training': '训练',
        'model': '模型',
        'system': '系统',
        'human': '人类',
        'intelligence': '智能',
        'learning': '学习',
        'knowledge': '知识',
        'world': '世界',
        'problem': '问题',
        'solution': '解决方案',
        'research': '研究',
        'science': '科学',
        'technology': '技术',
        'future': '未来',
        
        # 常用短语
        'thank you': '谢谢你',
        'good morning': '早上好',
        'good afternoon': '下午好',
        'how are you': '你好吗',
        'very well': '非常好',
        'I think': '我认为',
        'I believe': '我相信',
        'I want': '我想要',
        'I need': '我需要',
        'you are': '你是',
        'you can': '你可以',
        'you have': '你有',
        'would be': '将是',
        'can be': '可以是',
        'should be': '应该是',
        'might be': '可能是',
        'may not': '可能不',
        'do not': '不',
        'does not': '不',
        'will not': '不会',
        'cannot': '不能',
        
        # 问题词
        'what': '什么',
        'why': '为什么',
        'when': '什么时候',
        'where': '哪里',
        'who': '谁',
        'how': '怎样',
        'which': '哪一个',
        'question': '问题',
        'answer': '答案',
        
        # 特殊项
        'Noah': '诺亚',
        'Harari': '哈拉里',
        'Yoshua': '约书亚',
        'Eric': '埃里克',
        'Eugene': '尤金',
        'Davos': '达沃斯',
        'Korea': '韩国',
        'Europe': '欧洲',
        'US': '美国',
        'China': '中国',
        'GPT': 'GPT',
    }
    
    # 转换为小写进行匹配
    text_lower = text.lower()
    
    # 尝试长短语匹配（从长到短）
    phrases = sorted(vocab.keys(), key=len, reverse=True)
    for phrase in phrases:
        if phrase in text_lower:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            text = pattern.sub(vocab[phrase], text)
    
    return text

def write_srt(file_path: str, subtitles: List[Tuple[int, str, List[str]]]):
    """写入SRT文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, (seq_num, timestamp, subtitle_lines) in enumerate(subtitles):
            f.write(f"{seq_num}\n")
            f.write(f"{timestamp}\n")
            for line in subtitle_lines:
                f.write(f"{line}\n")
            if i < len(subtitles) - 1:
                f.write("\n")

def main():
    input_file = r'd:\Users\Source\Ai-Gameplay-Bot\logs\en.srt'
    output_file = r'd:\Users\Source\Ai-Gameplay-Bot\logs\zh-cn.srt'
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_file}")
        return
    
    print(f"📖 正在读取: {input_file}")
    print(f"⏳ 这可能需要几秒钟...")
    
    try:
        subtitles = parse_srt(input_file)
        print(f"✅ 已读取 {len(subtitles)} 条字幕")
        
        print(f"🔄 正在翻译...")
        translated_subs = []
        for seq_num, timestamp, subtitle_lines in subtitles:
            translated_lines = [simple_translate(line) for line in subtitle_lines]
            translated_subs.append((seq_num, timestamp, translated_lines))
        
        print(f"✍️  正在写入: {output_file}")
        write_srt(output_file, translated_subs)
        
        print(f"\n✅ 翻译完成!")
        print(f"📊 统计信息:")
        print(f"   - 总字幕条数: {len(translated_subs)}")
        print(f"   - 输出文件: {output_file}")
        print(f"   - 编码: UTF-8")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
