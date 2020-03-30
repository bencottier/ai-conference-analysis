import scrapy


class NeurIPS2019PapersSpider(scrapy.Spider):
    name = 'papers'
    n_papers = 0
    n_papers_with_code = 0

    start_urls = [
        'https://papers.nips.cc/book/advances-in-neural-information-processing-systems-32-2019',
    ]

    def closed(self, reason):
        print("Total papers:", self.n_papers)
        print("Papers with code:", self.n_papers_with_code)
        print("Percentage:", 100 * self.n_papers_with_code / self.n_papers)

    def parse(self, response):
        title = response.css('title::text').get()
        if '2019 proceedings' in title.lower():
            for paper in response.xpath('body/div/div/ul/li'):
                self.n_papers += 1

                next_page = paper.css('a::attr(href)').get()
                if next_page is not None:
                    next_page = response.urljoin(next_page)
                    yield scrapy.Request(next_page, callback=self.parse)
        else:
            for item in response.xpath('body/div/div/a'):
                item_text = item.css('a::text').get()
                if '[PDF]' in item_text:
                    pdf = item.css('a::attr(href)').get()
                    if pdf is not None:
                        pdf = response.urljoin(pdf)
                if '[Sourcecode]' in item_text:
                    self.n_papers_with_code += 1
                    code = True
                else:
                    code = False
            authors = response.css('li.author *::text').getall()
            yield {
                'title': title, 
                'authors': authors,
                'code': code, 
                'pdf': pdf
            }
