import logging
import time
import requests
import xlsxwriter
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from scrapy.utils.log import configure_logging

process = CrawlerProcess({
	'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

logging.getLogger('scrapy').propagate = False

busca = "https://www.falabella.com.pe/falabella-pe/search/?Ntt="
base = "https://falabella.scene7.com/is/image/FalabellaPE/"
img = "https://falabella.scene7.com/is/image/FalabellaPE/defaultPE?&wid=25&hei=25"
imagen = requests.get(img).content

tiene_pub = []
no_tiene_pub = []
errores = []
prods = []
sku_prod = []
marcas = []
sku_marca = []
tiene_img = []
no_tiene_img = []

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
			url = response.url
			url_prod = url.replace("product/","")
			req_url = response.meta['item']['start_url']
			sku = response.meta['item']['sku']

			MARCA_SELECTOR = 'h6 ::text'
			marca = response.css(MARCA_SELECTOR).extract_first()

			if url == 'https://www.falabella.com.pe/falabella-pe/':
				no_tiene_pub.append(sku)
			elif url.find("noSearchResult") != -1:
				no_tiene_pub.append(sku)
			elif url == req_url:
				no_tiene_pub.append(sku)
			else:
				tiene_pub.append(sku)
				sku_marca.append(sku)
				marcas.append(marca)
				if url_prod.find("prod") != -1:
					sku_prod.append(sku)
					prods.append(re.search('prod(.+?)/', url).group(0).replace("/",""))
				else:
					sku_prod.append(sku)
					prods.append(sku)
		except:
			errores.append(sku)


class FalabellaSkuImageSpider(scrapy.Spider):
	start_urls = []
	name = "fallabela_sku_image_spider"

	f = open('Lista')
	lista =f.read().splitlines()
	for prod in lista:
		start_urls.append([base+prod+"?&wid=25&hei=25",prod])
	
	# override method
	def start_requests(self):
		for url in self.start_urls:
			item = {'start_url': url[0], 'sku' : url[1]}
			request = Request(url[0], dont_filter=True)
			# set the meta['item'] to use the item in the next call back
			request.meta['item'] = item
			yield request

	def parse(self, response):
		url = response.url
		sku = response.meta['item']['sku']
		if response.body == imagen:
			no_tiene_img.append(sku)
		else:
			tiene_img.append(sku)


process.crawl(FalabellaSkuDataSpider)
process.crawl(FalabellaSkuImageSpider)
process.start()

print(time.time() - start)
print('procese calculos')

#genero reporte
s1 = pd.Series(tiene_pub, name='Publicado: Si')
s2 = pd.Series(no_tiene_pub, name='Publicado: No')
s3 = pd.Series(tiene_img, name='Imagen: Si')
s4 = pd.Series(no_tiene_img, name='Imagen: No')
df = pd.concat([s1,s2,s3,s4], axis=1)

s5 = pd.Series(sku_prod, name='SKU')
s6 = pd.Series(prods, name='Prod')
df2 = pd.concat([s5,s6], axis=1)

s10 = pd.Series(errores, name='SKU')
df4 = pd.concat([s10], axis=1)

s11 = pd.Series(sku_marca, name='SKU')
s12 = pd.Series(marcas, name='Marca')
df5 = pd.concat([s11,s12], axis=1)

writer_orig = pd.ExcelWriter('Resultado.xlsx', engine='xlsxwriter')

#Hoja 1
df.to_excel(writer_orig, index=False, sheet_name='Resultado',startrow=1)
workbook = writer_orig.book
worksheet = writer_orig.sheets['Resultado']
worksheet.set_column('A:D', 15)
worksheet.set_zoom(80)
merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#808080'})
worksheet.merge_range('A1:B1', 'Publicado', merge_format)
worksheet.merge_range('C1:D1', 'Imagen', merge_format)

#Hoja 2
df2.to_excel(writer_orig, index=False, sheet_name='Prods',startrow=1)
worksheet = writer_orig.sheets['Prods']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)
merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#FFFF00'})
worksheet.merge_range('A1:B1', 'Publicado', merge_format)

#Hoja 4
df4.to_excel(writer_orig, index=False, sheet_name='Errores',startrow=1)
worksheet = writer_orig.sheets['Errores']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)
cell_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#FF0000'})
worksheet.write('A1', "Errores", cell_format)

#Hoja 5
df5.to_excel(writer_orig, index=False, sheet_name='Marcas',startrow=1)
worksheet = writer_orig.sheets['Marcas']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)

writer_orig.save()

print(time.time() - start)
print('Finalizó el proceso')
