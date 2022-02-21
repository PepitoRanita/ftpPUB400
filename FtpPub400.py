import os, datetime, shutil, getpass, time, sys 
from ftplib import FTP
import tkinter as tk 
from tkinter import filedialog

def askDwnFolder(dialog):
	''' Pide el directorio donde se descargarán los archivos 
	devuelve el direcorio.
	args: dialogo a mostrar (string)'''
	print(dialog)
	# Escondemos la root de tk para que no moleste
	root = tk.Tk()
	root.withdraw()
	time.sleep(2.5)
	dst = filedialog.askdirectory()	 
	return dst

def askUsrPsw(usrprompt):
	''' Pide el usuario y password del PUB400
	devuelve user y pass
	args: dialogo a mostrar (string)'''
	user = input(usrprompt)
	passw = getpass.getpass()
	return user, passw

def getFileNamesFromDir(ftpserv, ftpdir):
	''' Nos devuelve SOLO los nombres los ficheros tras ejecutar un dir
	ya que si no tienen info como permisos etc. 
	devuelve una lista con solo los nombres 
	args:
	Servidor ftp (ftplib), directorio donde queremos hacer la operación en el servidor ftp (string con path)'''
	filelist = []
	ftpserv.cwd(ftpdir)
	ftpserv.dir(filelist.append)
	for file in filelist:
		filelist[filelist.index(file)] = file[54:] 
	return filelist

def createFoldersFromNameList(filelist, dstfldr):
	''' Crea carpetas según un listado de nombres 
	args:
	Lista de ficheros (list), donde queremos crearlos (string con path)'''
	for file in filelist:
		try:
			os.mkdir(os.path.join(dstfldr,file))
			print('El directorio {0} no existe, creandolo...'.format(os.path.basename(os.path.join(dstfldr,file))))
		except:
			continue


def memberDownload(ftpserv, filelist, ftpdir, dstfldr):
	''' Descarga todos los miembros de un AS400 según una lista de FILES 
	args: ftpserv (ftplib), lista de files (lista), directorio en el AS400 (string path), directorio destino local (string path) '''	
	for file in filelist:
		pathname=os.path.join(dstfldr,file)
		ftppath=ftpdir+file
		memberList=getFileNamesFromDir(ftpserv,ftppath)
		for member in memberList:
			try:
				print('Downloading member {0} from file {1} into folder {2} ...'.format(member,file,pathname))
				localfile=open(os.path.join(pathname,member),'wb')
				ftpserv.retrbinary('RETR ' + member,localfile.write,1024)
				localfile.close()
			except:
				print('Error getting members from {0} must be a savefile or similar, no members can be retrieved'.format(file))
				continue
		
			
# Se deja en variable para modificar por si hay que bajar de otro AS400 
SERVER = "www.PUB400.com"

# Flow					
print("Este programa descargará todos los *FILE y miembros asociados a tu usuario en PUB400...")
print("Primero necesitaremos alguna info...")

# Declarar ftp y pedir carpeta al usuario
ftp=FTP(SERVER)
# Primero se pide carpeta al usuario, en caso de cerrar la ventana sin elegir salimos
downloadFolder = askDwnFolder("A que carpeta quieres descargar?")
if downloadFolder == "":
	print("No se ha elegido carpeta, saliendo...")
	sys.exit(1)

# Permitiremos 3 intentos de login, para eso iniciamos un contador
loginCount = 0
while loginCount < 3:
	try:						
		user, passw = askUsrPsw("Cual es tu usuario en PUB400?: ")						
		ftp.login(user=user,passwd=passw)
		# Si login bueno salimos del while
		break
	except:
		# Si hay un error al autenticar quitamos un intento y repetimos
		print("Error al autenticar el usuario, prueba de nuevo")
		loginCount += 1
		# Si finalmente se hacen 3 intentos, fuera
		if loginCount >= 3:
			print("Intentos de login agotados para el script")
			sys.exit(1)

# Para navegar a las librerías del AS/400 es necesario usar la notación /QSYS.LIB/LIBRERIA_DEL_USUARIO1.LIB
userDIR=f'/QSYS.LIB/{user}1.LIB/'
SRCFiles = getFileNamesFromDir(ftp, userDIR)
createFoldersFromNameList(SRCFiles, downloadFolder)
memberDownload(ftp, SRCFiles, userDIR, downloadFolder)
print("--- * Descarga finalizada * ---")
sys.exit(0)