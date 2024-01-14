import subprocess
import sys
import time
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
#@markdown # Encuentre su árbol familiar
#subprocess.check_call(['python', '-m', 'pip', 'install', 'lxml', 'webdriver_manager', 'pandas', 'chromedriver-autoinstaller'])
import warnings
warnings.filterwarnings('ignore')
def get_info(cedula):
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  chrome_driver_path = 'C:/Users/juanm/Documents/Respaldo/juanandres-montero/Family-Tree/arbol-familiar-costarricense/arbol-familiar-costarricense/packages/chromedriver.exe'
  driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
  driver.get('https://servicioselectorales.tse.go.cr/chc/consulta_cedula.aspx')
  driver.save_screenshot('screenshot.png')
  # Enter the cedula number
  box = driver.find_element('xpath','//*[@id="txtcedula"]')
  box.send_keys(cedula)
  driver.find_element('xpath','//*[@id="btnConsultaCedula"]').click()
  time.sleep(1)
  driver.find_element('xpath','//*[@id="LinkButton11"]').click()
  time.sleep(1)
  table = driver.find_element('xpath', '//*[@id="form1"]/table[2]')
  rows = table.find_elements('xpath','//*[@id="form1"]/table[2]/tbody/tr')
  df = pd.read_html(table.get_attribute('outerHTML'))
  driver.find_element('xpath','//*[@id="ImageConsultaCedula"]').click()
  time.sleep(1)
  return df

def get_info_by_name(nombre,apellido1,apellido2):
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(options=options)
  driver.get('https://servicioselectorales.tse.go.cr/chc/consulta_nombres.aspx')
  # Enter the cedula number
  box = driver.find_element('xpath','//*[@id="txtnombre"]')
  box.send_keys(nombre)
  box = driver.find_element('xpath','//*[@id="txtapellido1"]')
  box.send_keys(apellido1)
  box = driver.find_element('xpath','//*[@id="txtapellido2"]')
  box.send_keys(apellido2)
  driver.find_element('xpath','//*[@id="btnConsultarNombre"]').click()
  time.sleep(4)

  driver.find_element('xpath','//*[@id="chk1_0"]').click()

  driver.find_element('xpath','//*[@id="Button1"]').click()

  time.sleep(1)
  ced = driver.find_element('xpath', '//*[@id="lblcedula"]')
  ced = ced.text
  return ced

def format(df):
  df_transposed = df.transpose()
  if df_transposed.empty:
    return df_transposed
  f0 = df_transposed.iloc[[0]]
  f1 = df_transposed.iloc[[1]]
  f2 = df_transposed.iloc[[2]]
  f3 = df_transposed.iloc[[3]]
  df0 = pd.concat([f0, f1], axis=0)
  df1 = pd.concat([f2, f3], axis=0)
  df1 = df1.reset_index()
  new_df = pd.concat([df0, df1], axis=1)
  new_df = new_df.drop(columns=['index'])
  new_df.columns = new_df.iloc[0]
  new_df = new_df.drop(0)
  new_df = new_df.dropna(axis=1, how='all')
  return new_df
#@markdown - Ingrese su número de cédula.

def tree(data,yo):
  padre = data.iloc[0, 7]
  madre = data.iloc[0, 9]

  padre_c = data.iloc[0, 8]  # (fila 0, columna 9)
  madre_c = data.iloc[0, 10]
  print(f"Padre de {yo}: {padre}")
  print(f"Madre de {yo}: {madre}")
  if madre_c.isalpha() or padre_c.isalpha():
    cedulas = None
    return cedulas
  if padre_c == '0':
    partes_nombre = padre.split()
    if len(partes_nombre) > 3:
      nombre = partes_nombre[0] + " " + partes_nombre[1]
      apellido1 = partes_nombre[2]
      apellido2 = partes_nombre[3]
      padre_c = get_info_by_name(nombre,apellido1,apellido2)
    elif len(partes_nombre) == 2:
      nombre = partes_nombre[0]
      apellido1 = partes_nombre[1]
      ### Fix
      padre_c = ""
    else:
      nombre = partes_nombre[0]
      apellido1 = partes_nombre[1]
      apellido2 = partes_nombre[2]
      padre_c = get_info_by_name(nombre,apellido1,apellido2)
  if madre_c == '0':
    partes_nombre = madre.split()
    if len(partes_nombre) > 3:
      nombre = partes_nombre[0] + " " + partes_nombre[1]
      apellido1 = partes_nombre[2]
      apellido2 = partes_nombre[3]
      madre_c = get_info_by_name(nombre,apellido1,apellido2)
    elif len(partes_nombre) == 2:
      nombre = partes_nombre[0]
      apellido1 = partes_nombre[1]
      ### Fix
      madre_c = ""
    else:
      nombre = partes_nombre[0]
      apellido1 = partes_nombre[1]
      apellido2 = partes_nombre[2]
      madre_c = get_info_by_name(nombre,apellido1,apellido2)
  if madre_c == "":
    cedulas = padre_c
  elif padre_c == "":
    cedulas = madre_c
  elif padre_c and madre_c == "":
    cedulas = None
  else:
    cedulas = padre_c,madre_c
  data = pd.DataFrame()
  return cedulas

def main():
  cedula = input("Ingrese numero de cedula: ") #@param {type:"string"}
  df = pd.DataFrame()
  df = df.append(get_info(cedula))
  try:
    print('hello')
    df = df.append(get_info(cedula))
  except Exception as e:
    print('Error: Invalid cedula number')
  data = pd.DataFrame()
  data = data.append(format(df))
  print(data)
  if not data.empty and data.shape[1] >= 2:
    yo = data.iloc[0, 1]
    print(f'Mi nombre es: {yo}')
    cedulas = tree(data,yo)
    ids = list(cedulas)
    while len(ids) > 0:
      for cedula in ids:
        df = pd.DataFrame()
        data = pd.DataFrame()
        df = df.append(get_info(cedula))
        data = data.append(format(df))
        yo = data.iloc[0, 1]
        tupla = tree(data,yo)
        try:
          lista_t = list(tupla)
        except:
          lista_t = None
        #try:
        if lista_t != None:
          ids.extend(lista_t)
          print(ids)
        #except:
          #print(f'Los padres de {yo} no tienen la cedula registrada en el TSE')
        data = pd.DataFrame()
        df = pd.DataFrame()

#if __name__ == '__main__':
main()
#@markdown *Código utiliza solo la información disponible en el TSE