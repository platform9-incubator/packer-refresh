import openstack
import json
from operator import itemgetter
from packerpy import PackerExecutable


IMAGE_NAME='centos-7'
IMAGE_SSH_USERNAME='centos'
PACKER_EXECUTABLE_PATH='/usr/local/bin/packer'
PACKER_TEMPLATE_PATH='/root/packer/template.json'
PACKER_BUILD_PATH='/root/packer/build.json'

# Initialize cloud
conn = openstack.connect(cloud='cloud')

print("Getting all images.")
images = conn.image.images()

packer_images = []

print("Looping through images and finding packer created ones")
for image in images:
  if IMAGE_NAME in image['name']:
    if "packer_created" in image['tags']:
      print("Found a packer created image and adding it to the list (Name: {})".format(image['name']))
      packer_images.append(image)

sorted_images = sorted(packer_images, key=itemgetter('created_at'), reverse=True)

print("Found {} Image(s)".format(len(sorted_images)))

while len(sorted_images) >= 5:
  print("There are too many images to save them all...")
  del_image = sorted_images[-1]
  print("Deleting image {} (ID: {})".format(del_image['name'], del_image['id']))
  conn.image.delete_image(del_image, ignore_missing=False)
  del sorted_images[-1]

for image in sorted_images:
  if "{}-latest".format(IMAGE_NAME) in image['name']:
    print("Renaming latest image to it's created date")
    new_image_name="{}-{}.img".format(IMAGE_NAME, image['created_at']).replace(':', '-')
    conn.image.update_image(image, name=new_image_name)

    print("Seting up the Packer Template files")
    with open(PACKER_TEMPLATE_PATH) as f:
      s = f.read()

    # Safely write the changed content, if found in the file
    with open(PACKER_BUILD_PATH, 'w+') as f:
      s = s.replace('__SOURCE_IMAGE_NAME__', new_image_name)
      s = s.replace('__IMAGE_NAME__', "{}-latest.img".format(IMAGE_NAME)) 
      s = s.replace('__IMAGE_SSH_USERNAME__', IMAGE_SSH_USERNAME)
      f.write(s)
print("Building a new Latest Image!")
print("This is very black box and takes a long time!")
PackerExecutable(config={'executable_path': PACKER_EXECUTABLE_PATH}).build(PACKER_BUILD_PATH)
new_image = conn.image.find_image("{}-latest.img".format(IMAGE_NAME))
conn.image.add_tag(new_image,'packer_created')

print("New Image created! ID: {}".format(new_image['id']))
