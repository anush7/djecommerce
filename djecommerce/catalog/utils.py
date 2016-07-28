from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from decimal import Decimal
from django.core.cache import cache
from django.template.defaultfilters import slugify
from products.models import Product

def image_cropper(data, LogoObject):
    try:
        path = LogoObject.image.path
        image = Image.open(path)
        zoom = Decimal(data['zoom'])
        top = int(-Decimal(data['cover_y1']))/ zoom
        left = int(-Decimal(data['cover_x1']))/ zoom
        print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        print top
        print left
        print "ggggg"
        width = image.size[0]
        height = image.size[1]
        right = left + (800 / zoom)
        bottom = top + (300 / zoom)

        print width
        print right
        print height
        print bottom
        print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

        if width < right:
            right = width
            left = 0
        if height < bottom:
            bottom = height
            top = 0

        box = (left, top, right, bottom)
        image = image.crop(box)
        image = image.resize((800, 300), Image.ANTIALIAS)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0)
        image = image.filter(ImageFilter.DETAIL)
        image.save(path,quality=90,optimised=True)
        try: cache.clear()
        except: pass
        return image
    except:
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
