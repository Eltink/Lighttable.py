from brackets_sorter import *

def brackets_rejoiner(filename):
	# Defining working dirs, if not available
	source_dir = 'C:\\Users\\glauc\\Desktop\\kjaf'
	try:
		os.makedirs(source_dir + "\\sel")
	except:
		pass
	dest_dir = os.path.join(source_dir, "sel")

	sequential = filename.split('.')[0] #Removing file format
	EV = ExposureBiasValue(filename)

	# Searching for target darker file
	target = str(sequential - 1) + "." + filename.split('.')[1]
	# TODO if is_number(a) -> append 
	try:
		if   ExposureBiasValue(target) == EV - 3: copia_arquivo(source_dir, target, dest_dir)
		elif ExposureBiasValue(target) == EV - 2: copia_arquivo(source_dir, target, dest_dir)
		elif ExposureBiasValue(target) == EV - 1: copia_arquivo(source_dir, target, dest_dir)
		else: pass # Couldnt find the darker file
		# TODO check it if was a backeting, if so, raise a warning
	except: pass

	try:
		if   EV() + 3 == EV:
			copia_arquivo(source_dir, target, dest_dir)
		elif EV() + 2 == EV:
			copia_arquivo(source_dir, target, dest_dir)
		elif EV() + 1 == EV:
			copia_arquivo(source_dir, target, dest_dir)
		else: pass # Couldnt find the lighter file
		# TODO check it if was a backeting, if so, info incomplete bracketing
	except: pass