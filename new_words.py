import json
import pdfplumber
import re
import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()


def load_word_list(json_file):
    """加载单词表"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(word.lower() for word in data.get('words', []))


def extract_lemmas_with_positions(pdf_file):
    """提取词根并记录首次出现的位置信息（页码、行号、单词序号）"""
    # 确保必要资源
    required_resources = ['punkt', 'wordnet', 'averaged_perceptron_tagger']
    for resource in required_resources:
        try:
            nltk.data.find(f'taggers/{resource}' if 'tagger' in resource else f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource)

    # 存储词根首次出现的位置：{lemma: (page_num, line_num, word_pos)}
    lemma_positions = {}
    # 存储按首次出现顺序排列的词根
    ordered_lemmas = []

    with pdfplumber.open(pdf_file) as pdf:
        total_pages = len(pdf.pages)
        print(f"开始处理PDF，共{total_pages}页...")

        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                print(f"第{page_num}页：无文本内容，跳过")
                continue

            # 按行分割并过滤空行
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            total_lines = len(lines)
            print(f"第{page_num}页：共{total_lines}行文本")

            for line_num, line in enumerate(lines, start=1):
                # 提取当前行的所有单词（保留原始顺序）
                words = re.findall(r"\b[a-zA-Z']+\b", line)
                cleaned_words = [word.lower().strip("'") for word in words if len(word.strip("'")) > 1]

                # 遍历行中的每个单词（记录在该行中的位置）
                for word_pos, word in enumerate(cleaned_words, start=1):
                    # 词形还原
                    lemma = lemmatizer.lemmatize(word, pos='v')
                    if lemma == word:
                        lemma = lemmatizer.lemmatize(word, pos='n')

                    # 仅记录首次出现的词根
                    if lemma not in lemma_positions:
                        lemma_positions[lemma] = (page_num, line_num, word_pos)
                        ordered_lemmas.append(lemma)
                        print(f"新词根：{lemma}（第{page_num}页，第{line_num}行，第{word_pos}个）")

        print("PDF处理完成！")

    return ordered_lemmas, lemma_positions


def filter_and_format_new_words(word_set, ordered_lemmas, lemma_positions):
    """筛选新词并格式化（添加位置注释）"""
    formatted_words = []
    for lemma in ordered_lemmas:
        if lemma not in word_set:
            # 获取位置信息
            page, line, pos = lemma_positions[lemma]
            # 格式化为："单词  # 第X页，第Y行，第Z个"
            formatted = f"{lemma}  # 第{page}页，第{line}行，第{pos}个"
            formatted_words.append(formatted)
    return formatted_words


def save_results(formatted_words, output_file):
    """保存带位置注释的结果"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # 注意：JSON中不支持真正的注释，这里将注释作为字符串的一部分
        json.dump({"new_words": formatted_words}, f, ensure_ascii=False, indent=2)
    print(f"\n处理完成！共{len(formatted_words)}个新词，已保存到{output_file}")


if __name__ == "__main__":
    word_list_path = "words_only.json"
    pdf_path = "A-Brief-History-of-Humankind.pdf"
    output_path = "new_words_with_positions.json"

    base_words = load_word_list(word_list_path)
    ordered_lemmas, lemma_positions = extract_lemmas_with_positions(pdf_file=pdf_path)
    formatted_new_words = filter_and_format_new_words(base_words, ordered_lemmas, lemma_positions)
    save_results(formatted_new_words, output_path)
