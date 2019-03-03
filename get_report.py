import requests
import pandas as pd
import xlsxwriter
import re
import time
from multiprocessing import Pool
from bs4 import BeautifulSoup

start = time.time()

img = "https://falabella.scene7.com/is/image/FalabellaPE/defaultPE?&wid=25&hei=25"
base = "https://falabella.scene7.com/is/image/FalabellaPE/"
imagen = requests.get(img).content

busca = "https://www.falabella.com.pe/falabella-pe/search/?Ntt="

def get_prod(pr):
	try:
		response = requests.head(busca+pr)
		if response.status_code != 302:
			return()
		url = response.headers['location'].replace("product/","")
		if url == 'https://www.falabella.com.pe/falabella-pe/':
			return ()
		if url.find("noSearchResult") != -1:
		  	return()
		if url.find("prod") != -1:
			return(pr,re.search('prod(.+?)/', url).group(0).replace("/",""))
		else:
			return(pr,pr)
	except:
		return(pr,pr)

def get_imag(prod):
	response = requests.get(base+prod+"?&wid=25&hei=25")
	if response.content == imagen:
		return(1,prod)
	else:
		return(2,prod)

def get_pub(prod):
	try:
		response = requests.head(busca+prod)
		if response.status_code != 302:
			return(0,prod)	   
		url = response.headers['location']
		if url == 'https://www.falabella.com.pe/falabella-pe/':
			return(1,prod)
		if url.find("noSearchResult") != -1:
	  		return(1,prod)
		else:
			return(2,prod)
	except:
		return(3,prod)

#Parte de skus
f = open('Lista')
lista =f.read().splitlines()
tiene_pub = []
no_tiene_pub = []
errores = []

#Parte de imagenes
imag = []
skus = []
tiene_img=[]
no_tiene_img=[]

#Parte de prods
prods = []

#Parte de cats
cats = []

end = time.time()
print(end - start)
print('procese lista')

if __name__ == '__main__':
	with Pool(16) as p:
		skus.append(p.map(get_pub, lista))
		end = time.time()
		print(end - start)
		print('procese pub')    
		imag.append(p.map(get_imag, lista))
		end = time.time()
		print(end - start)
		print('procese imag')
		prods.append(p.map(get_prod, lista))
		end = time.time()
		print(end - start)
		print('procese prods')
		#cats.append(p.map(get_cat, tiene_pub))
	end = time.time()
	print(end - start)
	print('procese funciones')

	prods[0] = list(filter(None, prods[0]))
	if prods[0] ==  []:
		prods[0] = [('','')]
	sku_prod, prod_prod = zip(*prods[0])
	#sku_cat, cat_cat, url_cat = zip(*cats[0])
	for sk in skus[0]:
		if sk[0] == 2:
			tiene_pub.append(sk[1])
		elif sk[0] == 1:
			no_tiene_pub.append(sk[1])
		else:
			errores.append(sk[1])

	for ima in imag[0]:
		if ima[0] == 2:
			tiene_img.append(ima[1])
		else:
			no_tiene_img.append(ima[1])

	end = time.time()
	print(end - start)
	print('procese calculos')

	s1 = pd.Series(tiene_pub, name='Publicado: Si')
	s2 = pd.Series(no_tiene_pub, name='Publicado: No')
	s3 = pd.Series(tiene_img, name='Imagen: Si')
	s4 = pd.Series(no_tiene_img, name='Imagen: No')
	df = pd.concat([s1,s2,s3,s4], axis=1)

	s5 = pd.Series(sku_prod, name='SKU')
	s6 = pd.Series(prod_prod, name='Prod')
	df2 = pd.concat([s5,s6], axis=1)

	s10 = pd.Series(errores, name='SKU')
	df4 = pd.concat([s10], axis=1)

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
	writer_orig.save()
  
	end = time.time()
	print(end - start)

	print('Finalizó el proceso')
