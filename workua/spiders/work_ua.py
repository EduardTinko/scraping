import scrapy


class WorkUaSpider(scrapy.Spider):
    name = "workua"

    start_urls = ["https://www.work.ua/jobs-it/?advs=1"]

    def parse_vacancy(self, response):
        title = response.xpath('//h1[@id="h1-name"]/text()').get()
        description = "".join(
            response.xpath(
                '//div[@id="job-description"]/descendant-or-self::*/text()'
            ).getall()
        )
        if "python" in title.lower() or "python" in description.lower():
            salary = (
                response.css(".glyphicon-hryvnia.glyphicon-large")
                .xpath("./following-sibling::span/text()")
                .get()
            )
            if salary:
                salary = (
                    salary.replace("\u202f", "")
                    .replace("\xa0", "")
                    .replace("\u2009", "")
                )
            else:
                salary = None
            employer = response.css(".hovered span::text").get()
            yield {
                "url": response.url,
                "title": title,
                "salary": salary,
                "employer": employer,
                "description": description.strip(),
            }

    def parse(self, response, **kwargs):
        for card in response.css(".card"):
            vacancy_url = card.css(".add-bottom").xpath("./h2/a/@href").get()
            if vacancy_url:
                yield response.follow(vacancy_url, callback=self.parse_vacancy)
        next_page = (
            response.css(".pagination ").xpath("./li")[-1].xpath("./a/@href").get()
        )
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
