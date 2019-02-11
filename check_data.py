#check if an sku has an image an if it is published

import requests
import pandas as pd
import xlsxwriter


skus = """
16550804
16578468
881214285
881214298
881214314
881417212
881419387
881420017
881417038
881423339
881423340
881423341
881423342
881423343
16598643
"""

#check for skus
busca = "https://www.falabella.com.pe/falabella-pe/search/?Ntt="
skus = skus.split("\n")
tiene_pub = []
no_tiene_pub = []

for prod in skus:
	if prod == "":
		continue
	response = requests.head(busca+prod)	   
	url = response.headers['location']
	if url.find("noSearchResult") != -1:
	  	no_tiene_pub.append(prod)
	else:
	   	tiene_pub.append(prod)


#check for images
imag = "https://falabella.scene7.com/is/image/FalabellaPE/defaultPE?&wid=25&hei=25"
base = "https://falabella.scene7.com/is/image/FalabellaPE/"
imagen = requests.get(imag).content
tiene_img = []
no_tiene_img = []

for prod in skus:
	if prod == "":
		continue
	response = requests.get(base+prod+"?&wid=25&hei=25")
	if response.content == imagen:
		no_tiene_img.append(prod)
	else:
		tiene_img.append(prod)

#save in .xlsx file
s1 = pd.Series(tiene_pub, name='Publicado: Si')
s2 = pd.Series(no_tiene_pub, name='Publicado: No')
s3 = pd.Series(tiene_img, name='Imagen: Si')
s4 = pd.Series(no_tiene_img, name='Imagen: No')
df = pd.concat([s1,s2,s3,s4], axis=1)

writer_orig = pd.ExcelWriter('Resultado.xlsx', engine='xlsxwriter')
df.to_excel(writer_orig, index=False, sheet_name='Resultado',startrow=1)
workbook = writer_orig.book
worksheet = writer_orig.sheets['Resultado']
worksheet.set_zoom(80)
worksheet.set_column('A:D', 15)
merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center', 'valign': 'vcenter','fg_color':'#808080'})
worksheet.merge_range('A1:B1', 'Publicado', merge_format)
worksheet.merge_range('C1:D1', 'Imagen', merge_format)
writer_orig.save()
