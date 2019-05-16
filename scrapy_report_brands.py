import logging
import time
import xlsxwriter
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request

process = CrawlerProcess({
	'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

logging.getLogger('scrapy').propagate = False

busca = "https://www.falabella.com.pe/falabella-pe/search/?Ntt="
base = "https://falabella.scene7.com/is/image/FalabellaPE/"

errores = []
marcas = []
sku_marca = []

start = time.time()

class FalabellaSkuDataSpider(scrapy.Spider):
	start_urls = []
	name = "fallabela_sku_data_spider"

	f = open('Lista')
	lista =f.read().splitlines()
	for prod in lista:
		start_urls.append([busca+prod,prod])

	# override method
	def start_requests(self):
		for url in self.start_urls:
			item = {'start_url': url[0], 'sku' : url[1]}
			request = Request(url[0], dont_filter=True)
			# set the meta['item'] to use the item in the next call back
			request.meta['item'] = item
			yield request

	def parse(self, response):
		try:
			sku = response.meta['item']['sku']
			MARCA_SELECTOR = 'h6 ::text'
			marca = response.css(MARCA_SELECTOR).extract_first()
			sku_marca.append(sku)
			marcas.append(marca)
		except:
			errores.append(sku)

process.crawl(FalabellaSkuDataSpider)
process.start()

print(time.time() - start)
print('procese calculos')

#genero reporte
s10 = pd.Series(errores, name='SKU')
df4 = pd.concat([s10], axis=1)

s11 = pd.Series(sku_marca, name='SKU')
s12 = pd.Series(marcas, name='Marca')
df5 = pd.concat([s11,s12], axis=1)

writer_orig = pd.ExcelWriter('Resultado.xlsx', engine='xlsxwriter')
workbook = writer_orig.book

#Hoja 1
df5.to_excel(writer_orig, index=False, sheet_name='Marcas',startrow=1)
worksheet = writer_orig.sheets['Marcas']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)

#Hoja 2
df4.to_excel(writer_orig, index=False, sheet_name='Errores',startrow=1)
worksheet = writer_orig.sheets['Errores']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)
cell_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#FF0000'})
worksheet.write('A1', "Errores", cell_format)

writer_orig.save()

print(time.time() - start)
print('Finalizó el proceso')
