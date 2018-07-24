from decimal import Decimal
class Pax:
    # Pax data from
    # http://www.azsolo.com/backup/index.php/car-classes-and-rules/pax-scoring-system
    # (Hyphens removed)
    FACTORS = dict( AM   = 1.000,
                    AS   = 0.814,
                    ASP  = 0.848,
                    BM   = 0.956,
                    BP   = 0.860,
                    BS   = 0.808,
                    BSP  = 0.846,
                    CAMC = 0.816,
                    CAMS = 0.831,
                    CAMT = 0.807,
                    CM   = 0.890,
                    CP   = 0.847,
                    CS   = 0.805,
                    CSP  = 0.857,
                    DM   = 0.895,
                    DP   = 0.858,
                    DS   = 0.794,
                    DSP  = 0.835,
                    EM   = 0.894,
                    EP   = 0.850,
                    ES   = 0.787,
                    ESP  = 0.828,
                    FM   = 0.904,
                    FP   = 0.863,
                    FS   = 0.797,
                    FSAE = 0.958,
                    FSP  = 0.819,
                    GS   = 0.786,
                    HCR  = 0.812,
                    HCS  = 0.791,
                    HS   = 0.781,
                    JA   = 0.855,
                    JB   = 0.825,
                    JC   = 0.718,
                    KM   = 0.928,
                    SM   = 0.853,
                    SMF  = 0.839,
                    SS   = 0.817,
                    SSC  = 0.806,
                    SSM  = 0.871,
                    SSP  = 0.852,
                    SSR  = 0.838,
                    STH  = 0.811,
                    STP  = 0.815,
                    STR  = 0.823,
                    STS  = 0.810,
                    STU  = 0.824,
                    STX  = 0.813,
                    XP   = 0.884,)



    @classmethod
    def factor(cls, car_class):
        car_class = car_class.upper()
        # Remove Ladies designation
        if car_class.endswith('L'):
            car_class = car_class[0:-1]
        factor = cls.FACTORS[car_class]
        return Decimal(str(factor))

