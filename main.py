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


def extract_pdf_lemmas_with_order(pdf_file):
    """提取PDF中的词根并记录首次出现顺序"""
    # 确保必要资源
    required_resources = ['punkt', 'wordnet', 'averaged_perceptron_tagger']
    for resource in required_resources:
        try:
            nltk.data.find(f'taggers/{resource}' if 'tagger' in resource else f'tokenizers/{resource}')
        except LookupError:
            nltk.download(resource)

    seen_lemmas = {}  # 记录词根首次出现的位置：{lemma: 首次出现的索引}
    current_index = 0  # 用于标记出现顺序

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # 提取并清洗单词
                words = re.findall(r"\b[a-zA-Z']+\b", text)
                cleaned_words = [word.lower().strip("'") for word in words if len(word.strip("'")) > 1]

                # 还原词根并记录首次出现顺序
                for word in cleaned_words:
                    # 词形还原（动词优先，再名词）
                    lemma = lemmatizer.lemmatize(word, pos='v')
                    if lemma == word:
                        lemma = lemmatizer.lemmatize(word, pos='n')

                    # 仅记录首次出现的词根
                    if lemma not in seen_lemmas:
                        seen_lemmas[lemma] = current_index  # 保存首次出现的索引
                        current_index += 1  # 索引递增

    # 返回按首次出现顺序排序的词根列表
    return sorted(seen_lemmas.keys(), key=lambda x: seen_lemmas[x])


def filter_new_lemmas(word_set, ordered_lemmas):
    """筛选不在单词表中的词根，保留原始顺序"""
    return [lemma for lemma in ordered_lemmas if lemma not in word_set]


def save_results(new_lemmas, output_file):
    """保存按首次出现顺序排列的结果"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"new_words": new_lemmas}, f, ensure_ascii=False, indent=2)
    print(f"处理完成！共找到{len(new_lemmas)}个新词根，按首次出现顺序排列，已保存到{output_file}")


if __name__ == "__main__":
    word_list_path = "words_only.json"  # 单词表JSON
    pdf_path = "A-Brief-History-of-Humankind.pdf"  # PDF文件
    output_path = "new_lemmas_ordered.json"  # 输出结果

    # 执行流程
    base_words = load_word_list(word_list_path)
    # 提取所有词根并按首次出现顺序排列
    ordered_lemmas = extract_pdf_lemmas_with_order(pdf_file=pdf_path)
    # 筛选不在单词表中的词根（保留顺序）
    new_lemmas = filter_new_lemmas(word_set=base_words, ordered_lemmas=ordered_lemmas)
    save_results(new_lemmas, output_path)
