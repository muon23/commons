import asyncio
import os
import unittest

from cj.utilities.Gpt3Portal import Gpt3Portal


class Gpt3PortalTest(unittest.TestCase):
    testText = """
nTianqiao Chen\n@Vincent 朱赟  volunteer 那个功能本身可以是调性的一个重要部分\n21:15\nTianqiao Chen\n调性并不是写写画画，有的时候可以从宣传小的贴心的功能开始\n21:16\nTianqiao Chen\n比方说我们的自动翻译，强调了人和人之间交流不应该有隔阂\n21:16\nTianqiao Chen\n比方说volunteer： 善良有爱心有责任心\n21:17\nTianqiao Chen\n@Evangeline Wang 如果你要好一些功能的调性，不要上来就说这个不对要改正那个\n21:17\nTianqiao Chen\n而是实实在在的增加一些小东西\n21:18\nTianqiao Chen\n而不要急着去改变一个东西。只要改变都会涉及到历史问题\n21:19\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n21:19\nTianqiao Chen\n千言万语，一个赞就够了，这个赞岂不是位置要更大一些？\n21:20\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n22:25\nJonathan\nTianqiao Chen\n@Jonathan 比方说我的那个👍，能不能就比所有竞品大，不但体现出潮，而且体现出简单深刻里面的简单这个特点！\n\n陈总这么一说，我有了创意，后面做成demo动效给陈总和大家看。\n22:49\nTianqiao Chen\n呵呵，以后不要等我“这么一说“\n22:50\nJonathan\n哦😄\n23:34\nEvangeline Wang\nTianqiao Chen\n@Evangeline Wang 这就是软装，这就是调性，多去找一些这些细节不断提升，拿出一个简易表出来\n\n明白，我明白陈总的意思了。我把值得优化的点逐个整理出来\n12/1/2022 7:43\nTianqiao Chen\n总结一下你想在tanka 用户里放的label，比方说乐于助人，有责任心\n7:44\nTianqiao Chen\n然后去找地方体现出来\n16:35\nEvangeline Wang\n明白\n

===
Summarize the text above using Chinese, separating key points in paragraphs.  Do not translate people names.:
    """

    async def __summarize(self):
        print("summarizing")
        gpt3 = Gpt3Portal.of(os.environ["OPENAI_KEY"])
        response = await gpt3.complete(self.testText, retries=2, temperature=0, max_tokens=500)
        print(response)

    async def __summarizeN(self, n):
        tasks = [
            asyncio.create_task(self.__summarize()) for _ in range(n)
        ]
        for i in range(n):
            print(f"summarize {i}")
            await tasks[i]

    def test_basic(self):
        asyncio.run(self.__summarizeN(2))

    def test_estimateTokens(self):
        text2test = self.testText
        text2test = """
        Pertama, ada masalah dengan versi yang baru sahaja dilancarkan. Ia menunjukkan gambar-gambar yang tidak diingini. Oleh itu, anda perlu memilih untuk hanya menunjukkan gambar-gambar terkini.\n\nKemudian, ada masalah dengan pengguna yang baru ditambah. Apabila pengguna itu dipadamkan, gambar profilnya masih akan dipaparkan pada pengguna yang baru. Oleh itu, Wang Linqing meminta bantuan untuk mengambil screenshot untuk membuktikan masalah ini.\n\nAkhirnya, Wu, Hua-Zheng menyatakan bahawa masalah ini akan dikaji semula oleh pihak produk. Mereka akan menimbang sama ada masalah ini perlu diubah menjadi permintaan. Pada hari yang sama, mesyuarat akan berlangsung lebih lambat sejam.
        """
        n = Gpt3Portal.estimateTokens(text2test)
        print(n)


if __name__ == '__main__':
    unittest.main()
