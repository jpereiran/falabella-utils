import requests
import pandas as pd
import xlsxwriter
import re
from bs4 import BeautifulSoup

lista = """
16550804
16578468
880276389
880276384
880276385
880276386
880276396
880737287
880737615
880276381
880738192
880738912
"""

#Parte de skus
busca = "https://www.falabella.com.pe/falabella-pe/search/?Ntt="
lista = lista.split("\n")
tiene_pub = []
no_tiene_pub = []
errores = []

for prod in lista:
	if prod == "":
		continue
	response = requests.head(busca+prod)
	if response.status_code != 302:
		errores.append(prod)
		continue	   
	url = response.headers['location']
	if url.find("noSearchResult") != -1:
	  	no_tiene_pub.append(prod)
	else:
	   	tiene_pub.append(prod)


#Parte de imagenes
imag = "https://falabella.scene7.com/is/image/FalabellaPE/defaultPE?&wid=25&hei=25"
base = "https://falabella.scene7.com/is/image/FalabellaPE/"
imagen = requests.get(imag).content
tiene_img = []
no_tiene_img = []

for prod in lista:
	if prod == "":
		continue
	response = requests.get(base+prod+"?&wid=25&hei=25")
	if response.content == imagen:
		no_tiene_img.append(prod)
	else:
		tiene_img.append(prod)


#Parte de prods
prods = []

for pr in tiene_pub:
	if pr == "":
		continue
	response = requests.head(busca+pr)
	url = response.headers['location'].replace("product/","")
	if url.find("prod") != -1:
		prods.append(re.search('prod(.+?)/', url).group(0).replace("/",""))
	else:
		prods.append(pr)

#Parte de cats
cats = []
subcats = []

for pr in tiene_pub:
  url = busca + pr
  cat, subcat = "", ""
  text = requests.get(url).text
  soup = BeautifulSoup(text, 'html.parser')
  scripts = soup.select('section div span span')
  cat =scripts[0].text.replace(" /  ","")
  if len(scripts) > 1:
      subcat = scripts[1].text.replace(" /  ","").replace("\n","")
  cats.append(cat)
  subcats.append(subcat)


s1 = pd.Series(tiene_pub, name='Publicado: Si')
s2 = pd.Series(no_tiene_pub, name='Publicado: No')
s3 = pd.Series(tiene_img, name='Imagen: Si')
s4 = pd.Series(no_tiene_img, name='Imagen: No')
df = pd.concat([s1,s2,s3,s4], axis=1)

s5 = pd.Series(tiene_pub, name='SKU')
s6 = pd.Series(prods, name='Prod')
df2 = pd.concat([s5,s6], axis=1)

s7 = pd.Series(tiene_pub, name='SKU')
s8 = pd.Series(cats, name='Categoría')
s9 = pd.Series(subcats, name='Subcategoría')
df3 = pd.concat([s7,s8,s9], axis=1)

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

#Hoja 3
df3.to_excel(writer_orig, index=False, sheet_name='Cats',startrow=1)
worksheet = writer_orig.sheets['Cats']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)
merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#FFFF00'})
worksheet.merge_range('A1:C1', 'Publicado', merge_format)


#Hoja 4
df4.to_excel(writer_orig, index=False, sheet_name='Errores',startrow=1)
worksheet = writer_orig.sheets['Errores']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)
cell_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#FF0000'})
worksheet.write('A1', "Errores", cell_format)
writer_orig.save()

print('Finalizó el proceso')
