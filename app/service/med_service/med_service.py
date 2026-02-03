from app.service import GatewayService

EXCLUDE_SERVICE = [
    "Рентген Оленегорск",
    "УЗИ Оленегорск",
    "Функциональная диагностика Стационар ММЦ",
    "Кабинет УЗИ Стационар ММЦ",
    "Рентгенография Стационар ММЦ",
    "Спирография Стационар ММЦ",
    "Поликлиника ММЦ УЗИ ВРТ",
    "Гематология Заозерск",
    "Биохимический Заозерск",
    "Рентген Заозерск",
    "Диагностика СПИДа Заозерск",
    "ЭКГ Заозерск",
    "Иммунология Заозерск",
    "Химико-микроскопические исследования Заозерск",
    "Инфекционная иммунология Заозерск",
    "Коагулогические исследования Заозерск",
    "ФЛЮ Заозерск",
    "КДЛ Островной",
    "Рентгеновский кабинет Островной",
    'ООО "МРТ -Эксперт Лидер"',
    "ГОБУЗ МОПД",
    "Патолого-анатомические исследования",
    "УЗИ Заозерск",
    "Инвитро Витамины",
    "Инвитро Диагностика остеопороза",
    "Инвитро Исследование клеща",
    "Инвитро VIP-профили для генетических исследований",
    "РГ стоматология ММЦ",
    "Узи Минина Оленегорск",
    "Функциональная диагностика Оленегорск",
    "Листы ожидания",
    "Маммография Оленегорск-2",
]


async def fetch_med_service_list(service: GatewayService):
    payload = {
        "params": {
            "c": "Reg",
            "m": "getDirectionMedServiceList",
        },
        "data": {
            "object": "MedService",
            "start": "0",
            "limit": "100",
            "Filter_Lpu_Nick": "ФГБУЗ ММЦ им. Н.И. Пирогова ФМБА России",
            "Filter_includeDopProfiles": "0",
            "ARMType": "regpol6",
            "FormName": "swDirectionMasterWindow",
            "DirType_Code": "9",
            "DirType_id": "10",
            "LpuUnitLevel": "1",
            "ListForDirection": "1",
            "isAutoAPLCovid": "0",
            "isSecondRead": "false",
            "isOnlyPolka": "0",
            "groupByMedService": "1",
        },
    }
    response = await service.request_json(json=payload)
    return [
        item for item in response if item.get("MedService_Name") not in EXCLUDE_SERVICE
    ]
