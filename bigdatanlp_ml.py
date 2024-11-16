# -*- coding: utf-8 -*-
"""BigDataNLP.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qoamRR-dSA0YWML6o5gXVB-B1C52vuDo
"""

from google.colab import drive
drive.mount('/content/drive')

"""# 텍스트 증강"""

from sklearn.model_selection import LeaveOneOut
import random

# 원본 데이터 불러오기
file_path = '/content/drive/MyDrive/Text Summariza/data/04.SUMMARY/summarized_documents.csv'
data = pd.read_csv(file_path)

print("원본 데이터 개수:", len(data))

# 랜덤 삭제 함수 정의
def random_deletion(text, p=0.3):
    words = text.split()
    if len(words) == 1:
        return text
    new_words = [word for word in words if random.uniform(0, 1) > p]
    return ' '.join(new_words) if new_words else words[random.randint(0, len(words) - 1)]

# 증강 데이터 생성
augmented_texts = []
for text in data['dialogue']:  # 'dialogue' 열 사용
    augmented_texts.append(random_deletion(text))  # 랜덤 삭제 적용

# 원본 데이터와 증강 데이터를 하나의 데이터프레임으로 결합
data_augmented = pd.DataFrame({
    'dialogue': data['dialogue'].tolist() + augmented_texts,  # 원문과 증강된 텍스트 결합
    'summary': data['summary'].tolist() + data['summary'].tolist()  # 요약은 그대로 복사
})

# 증강된 데이터 개수 확인
print("증강 후 데이터 개수:", len(data_augmented))

data_augmented.head()

len(data_augmented)

data = data_augmented.copy()

import re
from bs4 import BeautifulSoup
from konlpy.tag import Okt
from string import punctuation

tokenizer = Okt()

# 데이터 전처리 함수
def preprocess_sentence(sentence, remove_stopwords=True):
    sentence = sentence.lower()
    sentence = BeautifulSoup(sentence, "lxml").text
    sentence = re.sub(r'\([^)]*\)', '', sentence)
    sentence = re.sub('"','', sentence)
    sentence = re.sub("[^가-힣a-zA-Z\s]", " ", sentence)

    # URL 제거
    pattern = '(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    sentence = re.sub(pattern=pattern, repl='', string=sentence)

    # 기타 특수 문자 제거
    sentence = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', sentence)
    sentence = re.sub('\n', '.', sentence)

    words = tokenizer.morphs(sentence)

    # 불용어 제거
    if remove_stopwords:
        words = ' '.join(word for word in words if word not in final_stopwords and len(word) > 1)
    else:
        words = ' '.join(word for word in words if len(word) > 1)

    return words

clean_dialogue = []

for s in data['dialogue']:
    clean_dialogue.append(preprocess_sentence(s))

print("dialogue 전처리 후 결과: ", clean_dialogue[:1])

clean_summary = []

for s in data['summary']:
    clean_summary.append(preprocess_sentence(s, False))

print("summary 전처리 후 결과: ", clean_summary[:1])

data['dialogue_sentences'] = clean_dialogue
data['summary_sentences'] = clean_summary

data.replace('', np.nan, inplace=True)
print(data['dialogue_sentences'][0])

data.head()

!pip install transformers
!pip install datasets
!pip install evaluate
!pip install rouge-score
!pip install py7zr

# Transformers
from transformers import BartTokenizer, BartForConditionalGeneration
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments
from transformers import pipeline
from transformers import DataCollatorForSeq2Seq
import torch
import evaluate

from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

pd.set_option('display.max_colwidth', 20000)

seed = 42
colormap = 'cividis'
template = 'plotly_dark'

def display_feature_list(features, feature_type):

    print(f"\n{feature_type} Features: ")
    print(', '.join(features) if features else 'None')


def describe_df(df):

    global categorical_features, continuous_features, binary_features
    categorical_features = [col for col in df.columns if df[col].dtype == 'object']
    binary_features = [col for col in df.columns if df[col].nunique() <= 2 and df[col].dtype != 'object']
    continuous_features = [col for col in df.columns if df[col].dtype != 'object' and col not in binary_features]

    print(f"\n{type(df).__name__} shape: {df.shape}")
    print(f"\n{df.shape[0]:,.0f} samples")
    print(f"\n{df.shape[1]:,.0f} attributes")
    print(f'\nMissing Data: \n{df.isnull().sum()}')
    print(f'\nDuplicates: {df.duplicated().sum()}')
    print(f'\nData Types: \n{df.dtypes}')

    display_feature_list(categorical_features, 'Categorical')
    display_feature_list(continuous_features, 'Continuous')
    display_feature_list(binary_features, 'Binary')

    print(f'\n{type(df).__name__} Head: \n')
    display(df.head(5))
    print(f'\n{type(df).__name__} Tail: \n')
    display(df.tail(5))

def histogram_boxplot(df, hist_color, box_color, height, width, legend, name):

    features = df.select_dtypes(include = [np.number]).columns.tolist()

    for feat in features:
        try:
            fig = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=["Box Plot", "Histogram"],
                horizontal_spacing=0.2
            )

            density = gaussian_kde(df[feat])
            x_vals = np.linspace(min(df[feat]), max(df[feat]), 200)
            density_vals = density(x_vals)

            fig.add_trace(go.Scatter(x=x_vals, y = density_vals, mode = 'lines',
                                     fill = 'tozeroy', name="Density", line_color=hist_color), row=1, col=2)
            fig.add_trace(go.Box(y=df[feat], name="Box Plot", boxmean=True, line_color=box_color), row=1, col=1)

            fig.update_layout(title={'text': f'<b>{name} Word Count<br><sup><i>&nbsp;&nbsp;&nbsp;&nbsp;{feat}</i></sup></b>',
                                     'x': .025, 'xanchor': 'left'},
                             margin=dict(t=100),
                             showlegend=legend,
                             template = template,
                             #plot_bgcolor=bg_color,paper_bgcolor=paper_color,
                             height=height, width=width
                            )

            fig.update_yaxes(title_text=f"<b>Words</b>", row=1, col=1, showgrid=False)
            fig.update_xaxes(title_text="", row=1, col=1, showgrid=False)

            fig.update_yaxes(title_text="<b>Frequency</b>", row=1, col=2,showgrid=False)
            fig.update_xaxes(title_text=f"<b>Words</b>", row=1, col=2, showgrid=False)

            fig.show()
            print('\n')
        except Exception as e:
            print(f"An error occurred: {e}")

def plot_correlation(df, title, subtitle, height, width, font_size):

    corr = np.round(df.corr(numeric_only = True), 2)
    mask = np.triu(np.ones_like(corr, dtype = bool))
    c_mask = np.where(~mask, corr, 100)

    c = []
    for i in c_mask.tolist()[1:]:
        c.append([x for x in i if x != 100])



    fig = ff.create_annotated_heatmap(z=c[::-1],
                                      x=corr.index.tolist()[:-1],
                                      y=corr.columns.tolist()[1:][::-1],
                                      colorscale = colormap)

    fig.update_layout(title = {'text': f"<b>{title} Heatmap<br><sup>&nbsp;&nbsp;&nbsp;&nbsp;<i>{subtitle}</i></sup></b>",
                                'x': .025, 'xanchor': 'left', 'y': .95},
                    margin = dict(t=210, l = 110),
                    yaxis = dict(autorange = 'reversed', showgrid = False),
                    xaxis = dict(showgrid = False),
                    template = template,
                    #plot_bgcolor=bg_color,paper_bgcolor=paper_color,
                    height = height, width = width)


    fig.add_trace(go.Heatmap(z = c[::-1],
                             colorscale = colormap,
                             showscale = True,
                             visible = False))
    fig.data[1].visible = True

    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = font_size

    fig.show()

def compute_tfidf(df_column, ngram_range=(1,1), max_features=15):
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english', ngram_range=ngram_range)
    x = vectorizer.fit_transform(df_column.fillna(''))
    df_tfidfvect = pd.DataFrame(x.toarray(), columns=vectorizer.get_feature_names_out())
    return df_tfidfvect

describe_df(data)

!pip install plotly
!pip install numpy scipy

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde

df_text_lenght = pd.DataFrame()
for feat in categorical_features:
    df_text_lenght[feat] = data[feat].apply(lambda x: len(str(x).split()))

histogram_boxplot(df_text_lenght, '#89CFF0', '#00509E', 600, 1000, True, 'Dataset')

from sklearn.model_selection import train_test_split

# 80% train, 20% temp
train, temp = train_test_split(data, test_size=0.2, random_state=42)

# temp = 10% validation, 10% test
val, test = train_test_split(temp, test_size=0.5, random_state=42)

# 각 데이터셋의 크기 확인
print("Train shape:", train.shape)
print("Validation shape:", val.shape)
print("Test shape:", test.shape)

"""# Modeling"""

from transformers import BartTokenizer, BartForConditionalGeneration
from datasets import Dataset

checkpoint = 'gogamza/kobart-summarization'

tokenizer = BartTokenizer.from_pretrained(checkpoint)
model = BartForConditionalGeneration.from_pretrained(checkpoint)

print(model)

# 데이터 전처리 함수 정의
def preprocess_function(examples):
    inputs = [doc for doc in examples["dialogue"]]
    model_inputs = tokenizer(inputs, max_length=1024, truncation=True, padding="max_length")

    with tokenizer.as_target_tokenizer():
        labels = tokenizer(examples["summary"], max_length=128, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Pandas DataFrame을 Dataset 형식으로 변환
train_ds = Dataset.from_pandas(train)
test_ds = Dataset.from_pandas(test)
val_ds = Dataset.from_pandas(val)

# 데이터셋 전처리 및 토크나이징
tokenized_train = train_ds.map(preprocess_function, batched=True,
                               remove_columns=['dialogue', 'summary', 'dialogue_sentences', 'summary_sentences', '__index_level_0__'])
tokenized_test = test_ds.map(preprocess_function, batched=True,
                              remove_columns=['dialogue', 'summary', 'dialogue_sentences', 'summary_sentences', '__index_level_0__'])
tokenized_val = val_ds.map(preprocess_function, batched=True,
                             remove_columns=['dialogue', 'summary', 'dialogue_sentences', 'summary_sentences', '__index_level_0__'])

from evaluate import load

metric = load('rouge')

def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)

    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
    decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]

    result = metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)

    if isinstance(result, dict):
        result = {key: value.fmeasure * 100 for key, value in result.items() if hasattr(value, 'fmeasure')}
    else:
        result = {"rouge": result}

    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in predictions]
    result["gen_len"] = np.mean(prediction_lens)

    return {k: round(v, 4) for k, v in result.items()}

training_args = Seq2SeqTrainingArguments(
    output_dir = 'weekly_technology_trends',
    eval_strategy = "epoch",
    save_strategy = 'epoch',
    load_best_model_at_end = True,
    metric_for_best_model = 'eval_loss',
    seed = seed,
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=2,
    weight_decay=0.01,
    save_total_limit=2,
    num_train_epochs=4,
    predict_with_generate=True,
    fp16=True,
    report_to="none"
)

from transformers import PreTrainedTokenizerFast

tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-base-v1")

from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast, pipeline

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, padding='max_length', max_length=1024)

training_args = Seq2SeqTrainingArguments(
    output_dir="kobart_finetuned",
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    seed=42,
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=2,
    weight_decay=0.01,
    save_total_limit=2,
    num_train_epochs=8,
    predict_with_generate=True,
    fp16=True,
    logging_dir='./logs',
    logging_strategy="steps",
    logging_steps=40,
    report_to="none"
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

trainer.train()

from nltk.tokenize import sent_tokenize
import re

text = data['dialogue'][10] if 10 < len(data['dialogue']) else ""
reference_summary = data['summary'][10] if 10 < len(data['summary']) else ""

if not text or not reference_summary:
    print("데이터셋에서 대화 또는 요약이 누락되었습니다.")
else:
    paragraphs = text.split("\n\n")
    max_input_length = 1024

    generated_summaries = []
    for i, paragraph in enumerate(paragraphs):
        if len(paragraph.strip()) == 0:
            continue

        tokenized_paragraph = tokenizer(paragraph.strip())['input_ids']
        if len(tokenized_paragraph) > max_input_length:
            sentences = sent_tokenize(paragraph)
            chunks = [
                " ".join(sentences[i:i + 5]) for i in range(0, len(sentences), 5)
            ]
        else:
            chunks = [paragraph.strip()]

        for j, chunk in enumerate(chunks):
            print(f"\n요약 생성 중: 문단 {i + 1}, 청크 {j + 1}/{len(chunks)}")
            summary = summarizer(chunk, max_length=150, min_length=50, do_sample=False, num_beams=5)
            generated_summaries.append(summary[0]['summary_text'])

    combined_summary = " ".join(generated_summaries)
    combined_summary = re.sub(r'(\b\w+\b)\s+\1', r'\1', combined_summary)  # 중복 단어 제거
    combined_summary = ". ".join([sent.capitalize() for sent in combined_summary.split(". ")])  # 문장 정리

import textwrap

# 결과 출력 함수 정의
def print_wrapped(label, text, width=80):
    # print(f"\n{label} (길이: {len(text)} 문자):\n")
    print(f"\n{label}")
    print("\n".join(textwrap.wrap(text, width)))

# 결과 출력
print_wrapped("참조 요약", reference_summary)
print_wrapped("생성된 요약", combined_summary)