from django import template

register = template.Library()

ROW_PER_PAGE = 5

@register.filter
def get_table_number(value, arg):
    return value + ( (arg - 1) * ROW_PER_PAGE)

# Pada kode diatas kita memanggil modul template dari Django, kemudian membuat sebuah variabel yang berisi sebuah objek template.Library(). Kemudian kita panggil decorator @register.filter untuk menandai function get_table_number sebagai function yang dapat dipanggil di suatu template. Di dalam function tersebut terdapat sebuah rumus yang akan menghitung penomoran di setiap halaman yang telah di beri pagination. Parameter value adalah baris data yang akan diproses, kemudian arg adalah halaman dimana Anda berada saat ini. Anda dapat melihat contoh perhitungan berikut:

#jangan disalin, hanya contoh perhitungan

# value = 1
# arg = 2
# nomor_baru = 1 + ( (2 - 1) * 5 )
# maka nomor_baru adalah 6

# value = 3
# arg = 1
# nomor_baru = 3 + ( (1 - 1) * 5 )
# maka nomor_baru adalah 3

# value = 3
# arg = 4
# nomor_baru = 3 + ( (3 - 1) * 5 )
# maka nomor_baru adalah 13