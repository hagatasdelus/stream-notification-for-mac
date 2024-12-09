# -*- coding: utf-8 -*-

__author__ = "Hagata"
__version__ = "0.0.1"
__date__ = "2024/12/08 (Created: 2024/10/20)"

class ConstantError(Exception):
    """Constantクラスの例外"""
    INHERITANCE_ERROR = "Can't inheritance of [{0}] and [{1}] together"
    COLLISION_ERROR = "Collision the constant [{0}]"
    REBIND_ERROR = "Can't rebind constant [{0}]"
    INSTANCE_ERROR = "Can't make instance of Constant class"
    ATTRIBUTE_ERROR = "Attribute [{0}] were not constant or not settable."
    SET_ERROR = "Can't set attribute to Constant [{0}]"

class ConstantMeta(type):
    """Constantクラスのメタクラス"""

    def __new__(cls, classname: str, bases: tuple, class_dict: dict) -> "ConstantMeta":
        # 異なるConstantMetaを継承していないか検証する
        sub_clses = [cls for cls in bases if isinstance(cls, ConstantMeta)]
        for sub_cls in sub_clses[1:]:
            if sub_clses[0] != sub_cls:
                raise ConstantError(
                    ConstantError.INHERITANCE_ERROR.format(
                        sub_clses[0].__name__, sub_cls.__name__
                    )
                )

        # 親クラス同士で定数の衝突が起こっていないか確認
        super_consts: set[str] = set()
        for base in bases:
            base_consts = ConstantMeta.__get_constant_attr(base.__dict__)
            collisions = (super_consts & base_consts)
            if collisions:
                collis_str = ", ".join(collisions)
                raise ConstantError(
                    ConstantError.COLLISION_ERROR.format(collis_str)
                )
            super_consts |= base_consts

        # 定義するクラスで定数の再定義をしていないか確認
        new_consts = ConstantMeta.__get_constant_attr(class_dict)
        rebinds = (super_consts & new_consts)
        if rebinds:
            rebinds_str = ", ".join(rebinds)
            raise ConstantError(ConstantError.REBIND_ERROR.format(rebinds_str))

        # __init__関数置き換えてインスタンス生成を禁止する
        def _meta__init__(*_):
            # インスタンスの生成をしようとした際、ConstantErrorを送出する。
            raise ConstantError(ConstantError.INSTANCE_ERROR)
        # __init__関数を置き換えてインスタンス生成を禁止する。
        class_dict["__init__"] = _meta__init__

        return type.__new__(cls, classname, bases, class_dict)

    @staticmethod
    def __get_constant_attr(class_dict: dict) -> set[str]:
        """定数として扱うアトリビュートの集合を取得する"""
        # 特殊なアトリビュートを除くアトリビュートを取得する
        attrs = {
            attr for attr in class_dict if not ConstantMeta.__is_special_func(attr)
        }
        # アトリビュートがすべて定数または例外的にクラス変数に格納可能な
        # 変数であることを確認する
        cnst_attr = {attr for attr in attrs if ConstantMeta.is_constant_attr(attr)}
        var_attr = {attr for attr in attrs if ConstantMeta.is_settable_attr(attr)}
        wrong_attr = attrs - (cnst_attr | var_attr)
        if wrong_attr:
            wrong_attr_str = ", ".join(wrong_attr)
            raise ConstantError(
                ConstantError.ATTRIBUTE_ERROR.format(wrong_attr_str)
            )
        return cnst_attr

    @staticmethod
    def __is_special_func(name):
        """特殊アトリビュートかどうかを判定する"""
        return name.startswith("__") and name.endswith("__")

    @classmethod
    def is_constant_attr(cls, name):
        """定数として扱うアトリビュートか判定する"""
        return (not name.startswith("__"))

    @classmethod
    def is_settable_attr(cls, name):
        """例外的にクラス変数に格納することを許可するアトリビュートか判定する"""
        return (not cls.is_constant_attr(name))

    def __setattr__(cls, name, value):
        cls_type = type(cls)
        if cls.is_constant_attr(name) or (not cls_type.is_settable_attr(name)):
            raise ConstantError(ConstantError.SET_ERROR.format(name))
        super().__setattr__(name, value)

class Constant(metaclass=ConstantMeta):
     """定数クラス"""


