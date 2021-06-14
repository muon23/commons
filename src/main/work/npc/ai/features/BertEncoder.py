import numpy as np
import transformers as tf

from work.npc.ai.utilities.Languages import Languages


#
# Known issues:
# - It seemed that you cannot create multiple BertEncoder at the same time.  Something in the BERT library would
#   overwrite earlier loaded models with the last one.
#

class BertEncoder:

    modelSpec = {
        # [ tokenizer class, model class, path to model in HuggingFace, languages applied ]
        "bert-base-chinese":
            [tf.AutoTokenizer, tf.AutoModelWithLMHead, None, ["zh"]],
        "distilbert-base-uncased":
            [tf.DistilBertTokenizer, tf.DistilBertModel, None, ["en"]],
        "bert-base-uncased":
            [tf.BertTokenizer, tf.BertModel, None, ["en"]],
        "distilbert-base-multilingual-cased":
            [tf.AutoTokenizer, tf.AutoModel, None, ["zh", "en"]],
        "roberta-large-mnli":
            [tf.AutoTokenizer, tf.AutoModel, None, ["en"]],
        "MiniLM-L12-H384-uncased":
            [tf.AutoTokenizer, tf.AutoModel, "microsoft", ["en"]],
        "xlm-r-100langs-bert-base-nli-stsb-mean-tokens":
            [tf.AutoTokenizer, tf.AutoModel, "sentence-transformers", ["zh", "en"]],
        "xlm-r-100langs-bert-base-nli-mean-tokens":
            [tf.AutoTokenizer, tf.AutoModel, "sentence-transformers", ["zh", "en"]],
        "distilbert-multilingual-nli-stsb-quora-ranking":
            [tf.AutoTokenizer, tf.AutoModel, "sentence-transformers", ["zh", "en"]],
        "Multilingual-MiniLM-L12-H384":
            [tf.XLMRobertaTokenizer, tf.AutoModel, "microsoft", ["zh", "en"]],
    }

    def __init__(self, modelName):
        if modelName not in BertEncoder.modelSpec:
            raise ValueError(f"unsupported model name {modelName}")

        tokenizer, model, path, self.languages = BertEncoder.modelSpec[modelName]
        if path:
            modelName = path + "/" + modelName

        self.tokenizer = tokenizer.from_pretrained(modelName)
        self.model = model.from_pretrained(modelName)

    def encodeSentences(self, text):
        ideoText, alphaText = Languages.separateIdeograph(text)
        hanSent = Languages.hanziSentences(ideoText)
        engSent = Languages.englishSentences(alphaText)

        sentences = (hanSent if "zh" in self.languages else []) + \
                    (engSent if "en" in self.languages else [])

        if len(sentences) == 0:
            return None, None

        tokenized = self.tokenizer(
            sentences,
            padding=True, max_length=512, truncation=True,
            add_special_tokens=True,
            return_tensors='pt'
        )

        # with torch.no_grad():
        #     lastHiddenStates = self.model(**tokenized)
        lastHiddenStates = self.model(**tokenized)

        return sentences, lastHiddenStates[0][:, 0, :].detach().numpy()

    def encode(self, text):
        sentences, vectors = self.encodeSentences(text)
        return np.mean(vectors, axis=0) if sentences else None

    def encode1(self, text):
        tokenized = self.tokenizer(
            [text],
            padding=True, max_length=512, truncation=True,
            add_special_tokens=True,
            return_tensors='pt'
        )

        lastHiddenStates = self.model(**tokenized)

        return lastHiddenStates[0][:, 0, :].detach().numpy()[0]

