from brackets_sorter import *
# import os

def brackets_rejoiner(filename, median_folder, output_folder):
	# Defining working dirs, if not available
	source_dir = 'C:\\Users\\glauc\\Desktop\\kjaf'
	dest_dir = os.path.join(source_dir, "brackets_rejoiner")

	sequential = filename.split('.')[0] #Removing file format
	EV = ExposureBiasValue(filename)

	# Searching for target darker file
	target_image = str(sequential - 1) + "." + filename.split('.')[1]
	target_image_path = os.path.join(median_folder, target_image)
	# TODO if is_number(a) -> append 
	try:
		if   ExposureBiasValue(target_image) == EV - 3: copia_arquivo(source_dir, target_image, dest_dir)
		elif ExposureBiasValue(target_image) == EV - 2: copia_arquivo(source_dir, target_image, dest_dir)
		elif ExposureBiasValue(target_image) == EV - 1: copia_arquivo(source_dir, target_image, dest_dir)
		else: print("Couldnt find the darker file. Sequential: ", sequential, "Target: ", target_image)
		# TODO check it if was a backeting, if so, raise a warning
	except: pass
	# Searching for target lighter file
	target_image = str(sequential + 1) + "." + filename.split('.')[1]
	try:
		if   ExposureBiasValue(target_image) == EV + 3: copia_arquivo(source_dir, target_image, dest_dir)
		elif ExposureBiasValue(target_image) == EV + 2: copia_arquivo(source_dir, target_image, dest_dir)
		elif ExposureBiasValue(target_image) == EV + 1: copia_arquivo(source_dir, target_image, dest_dir)
		else: print("Couldnt find the lighter file. Sequential: ", sequential, "Target: ", target)
		# TODO check it if was a backeting, if so, info incomplete bracketing
	except: pass

def find_associated_bracketed_images(database_folder, median_folder, output_folder):
	# Create the output folder if it doesn't exist
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	# Iterate over each file in the database folder
	for filename in os.listdir(database_folder):
		if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
			# Call the brackets_rejoiner function for the current file
			brackets_rejoiner(os.path.join(database_folder, filename), median_folder, output_folder)

# Example usage
database_folder = "path/to/database_folder"
median_folder = "path/to/median_folder"
output_folder = "path/to/Bracketed_outliers"

find_associated_bracketed_images(database_folder, median_folder, output_folder)