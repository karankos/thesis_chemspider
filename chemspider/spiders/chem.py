import scrapy
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.items import ChemspiderItem
import re

class ChemSpider(CrawlSpider):
    name = 'chem'
    allowed_domains = ['chemspider.com']
    start_urls = ['https://www.chemspider.com/Chemical-Structure.0001.html']

    rules = (Rule(callback='parse'),) 

    def parse(self, response):
        
        chem = ChemspiderItem()

        chem_id = response.url.split("/")[-1]

        #ID
        chem["chem_id"] = chem_id

        #Name
        name = response.xpath('//div[@class="structure-head"]/h1/span//text()').extract()
        chem["name"] = ''.join(name)

        #Molecular Formula
        molecular_formula = response.xpath('//div[@class="structure-head"]//ul//li').extract_first()
        mf = re.compile(r'<.*?>')
        molecular_formula = mf.sub('', molecular_formula)
        chem["mol_formula"] = molecular_formula.replace("Molecular Formula", "")

        #Synonyms
        synonyms = response.xpath(
            '//div[@id="ctl00_ctl00_ContentSection_ContentPlaceHolder1_RecordViewTabDetailsControl_identifiers_ctl_synonymsControl_SynonymsPanel"]//div//strong'
        ).extract()

        wbr = re.compile(r'<\/*wbr?>')
        strong = re.compile(r'<strong?>')

        synonyms = ''.join(synonyms)
        synonyms = wbr.sub('',synonyms)
        list_syn = list(synonyms.split("</strong>"))

        for idx,syn in enumerate(list_syn):
            syn = syn.replace(',', '')
            syn = strong.sub('',syn)
            list_syn[idx] = syn
        chem["synonyms"] = list_syn

        #Smiles
        smiles_1 = response.xpath('//div[@class="struct-extra-props"]//div//ul//span/descendant-or-self::text()')[5].extract()
        smiles_2 = response.xpath('//div[@class="struct-extra-props"]//div//ul//span/descendant-or-self::text()')[6].extract()
        chem["smiles"] = smiles_1 + smiles_2

        scrapped_info ={
            'name' : chem["name"],
            'chem_id' : chem["chem_id"],
            'smiles' : chem["smiles"],
            'molecular_formula' : chem["mol_formula"],
            'synonyms' : chem["synonyms"]
        }
        yield scrapped_info
