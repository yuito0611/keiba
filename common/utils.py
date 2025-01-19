def isfloat(s):  # 浮動小数点数値を表しているかどうかを判定
    try:
        float(s)  # 文字列を実際にfloat関数で変換してみる
    except ValueError:
        return False
    else:
        return True
    
def is_int(variable):
    try:
        int(variable)
        return True
    except ValueError:
        return False
    
def string2int(s):
    if is_int(s):
        return int(s)
    else:
        return int(s.replace(',', ''))  # カンマを削除して返す