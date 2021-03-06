import json
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from decimal import Decimal
from django.core.cache import cache
from django.template.defaultfilters import slugify
import decimal
from products.models import Product
from cStringIO import StringIO
from django.core.files.base import ContentFile

def image_cropper(data, img_file, LogoObject):
    try:
        inmemory_img = StringIO(img_file.read())
        image = Image.open(inmemory_img)

        zoom = Decimal(data['zoom'])
        top = int(-Decimal(data['cover_y1']))/ zoom
        left = int(-Decimal(data['cover_x1']))/ zoom
        print "1111111111111111111111111111111111111111111111111111"
        print 'zoom: ', zoom
        print 'top: ', top
        print 'left: ', left

        width = image.size[0]
        height = image.size[1]
        right = left + (450 / zoom)
        bottom = top + (450 / zoom)

        print 'width: ', width
        print 'right: ', right
        print 'height: ', height
        print 'bottom: ', bottom

        if width < right:
            right = width
            left = 0
        if height < bottom:
            bottom = height
            top = 0

        print "2222222222222222222222222222222222222222222222222222222222"
        print 'crop -> left, top, right, bottom'
        print left, top, right, bottom
        print "3333333333333333333333333333333333333333333333333333333333"

        box = (left, top, right, bottom)
        image = image.crop(box)
        image = image.resize((450, 450), Image.ANTIALIAS)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0)
        image = image.filter(ImageFilter.DETAIL)

        temp_handle = StringIO()
        image.save(temp_handle, "JPEG")
        temp_handle.seek(0)
        return temp_handle
    except:
        import sys
        print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        print sys.exc_info()
        print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
        return False

def get_unique_slug(title, Module, instance=False):
    key={}
    ori_slug = slugify(title)
    if instance:
        key['id']=instance.id
    try:
        Module.objects.exclude(**key).filter(slug=ori_slug)[0]
        count = 1
        while True:
            slug = ori_slug
            slug += str(count)
            try:Module.objects.exclude(**key).filter(slug=slug)[0]
            except:
                ori_slug = slug
                break
            count += 1
    except:pass
    return ori_slug


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


def get_rows(queryset, fields=[]):
    yield ([fld.title().replace('_',' ') for fld in fields])
    for item in queryset:
        yield ([getattr(item, fld) for fld in fields])








# def image_cropper1(data, LogoObject):
#     try:
#         path = LogoObject.image.path
#         image = Image.open(path)
#         zoom = Decimal(data['zoom'])
#         top = int(-Decimal(data['cover_y1']))/ zoom
#         left = int(-Decimal(data['cover_x1']))/ zoom
#         print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
#         print top
#         print left
#         print "ggggg"
#         width = image.size[0]
#         height = image.size[1]
#         right = left + (450 / zoom)
#         bottom = top + (450 / zoom)

#         print width
#         print right
#         print height
#         print bottom
#         print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

#         if width < right:
#             right = width
#             left = 0
#         if height < bottom:
#             bottom = height
#             top = 0

#         box = (left, top, right, bottom)
#         image = image.crop(box)
#         image = image.resize((450, 450), Image.ANTIALIAS)
#         if image.mode not in ('L', 'RGB'):
#             image = image.convert('RGB')
#         enhancer = ImageEnhance.Sharpness(image)
#         image = enhancer.enhance(1.0)
#         image = image.filter(ImageFilter.DETAIL)
#         image.save(path,quality=90,optimised=True)
#         try: cache.clear()
#         except: pass
#         return image
#     except:
#         import sys
#         print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
#         print sys.exc_info()
#         print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
#         return False



# def image_cropper2(data, LogoObject):
    # from storages.backends.s3boto import S3BotoStorage
    # from django.core.files.storage import default_storage as storage
    # from djecommerce.s3utils import CustomS3BotoStorage, MediaRootS3BotoStorage
    # custom_storage = CustomS3BotoStorage()
#     try:
#         file_path = LogoObject.image.name
#         print "111111111111111111111111111111111111111111111111111"
#         print file_path
#         f = custom_storage.open(file_path, 'r')
#         # f = storage.open(file_path, 'r')
#         # f = S3BotoStorage.open(file_path, 'r')
#         image = Image.open(f)

#         zoom = Decimal(data['zoom'])
#         top = int(-Decimal(data['cover_y1']))/ zoom
#         left = int(-Decimal(data['cover_x1']))/ zoom
#         print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
#         print zoom
#         print top
#         print left
#         print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

#         width = image.size[0]
#         height = image.size[1]
#         right = left + (450 / zoom)
#         bottom = top + (450 / zoom)

#         print width
#         print right
#         print height
#         print bottom
#         print "cccccccccccccccccccccccccccccccccccccccccccccccccccc"

#         if width < right:
#             right = width
#             left = 0
#         if height < bottom:
#             bottom = height
#             top = 0

#         box = (left, top, right, bottom)
#         image = image.crop(box)
#         image = image.resize((450, 450), Image.ANTIALIAS)
#         if image.mode not in ('L', 'RGB'):
#             image = image.convert('RGB')
#         enhancer = ImageEnhance.Sharpness(image)
#         image = enhancer.enhance(1.0)
#         image = image.filter(ImageFilter.DETAIL)

#         f_thumb = custom_storage.open(file_path, "w")
#         # f_thumb = storage.open(file_path, "w")
#         # f_thumb = S3BotoStorage.open(file_path, 'w')
#         image.save(f_thumb, "JPEG")
#         f_thumb.seek(0)
#         f_thumb.close()
#         print "2222222222222222222222222222222222222222222222222222222"
#         try: cache.clear()
#         except: pass
#         return image
#     except:
#         import sys
#         print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
#         print sys.exc_info()
#         print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
#         return False






