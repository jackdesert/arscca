from decimal import Decimal
class Pax:
    # Pax data from
    # http://solotime.info/pax/rtp2018.html
    # (Hyphens removed)
    FACTORS_2018 = dict( AM    = 1.000,
                         AS    = 0.814,
                         ASP   = 0.848,
                         BM    = 0.956,
                         BP    = 0.860,
                         BS    = 0.808,
                         BSP   = 0.846,
                         CAMC  = 0.816,
                         CAMS  = 0.831,
                         CAMT  = 0.807,
                         CM    = 0.890,
                         CP    = 0.847,
                         CS    = 0.805,
                         CSP   = 0.857,
                         DM    = 0.895,
                         DP    = 0.858,
                         DS    = 0.794,
                         DSP   = 0.835,
                         EM    = 0.894,
                         EP    = 0.850,
                         ES    = 0.787,
                         ESP   = 0.828,
                         FM    = 0.904,
                         FP    = 0.863,
                         FS    = 0.797,
                         FSAE  = 0.958,
                         FSP   = 0.819,
                         GS    = 0.786,
                         HCR   = 0.812,
                         HCS   = 0.791,
                         HS    = 0.781,
                         JA    = 0.855,
                         JB    = 0.825,
                         JC    = 0.718,
                         KM    = 0.928,
                         SM    = 0.853,
                         SMF   = 0.839,
                         SS    = 0.817,
                         SSC   = 0.806,
                         SSM   = 0.871,
                         SSP   = 0.852,
                         SSR   = 0.838,
                         STH   = 0.811,
                         STP   = 0.815,
                         STR   = 0.823,
                         STS   = 0.810,
                         STU   = 0.824,
                         STX   = 0.813,
                         XP    = 0.884,)

    # Pax data from
    # http://solotime.info/pax/rtp2019.html
    # (Hyphens removed)
    FACTORS_2019 = dict(
                        STM   = 0.833, # STM IS CUSTOM TO ARKANSAS

                        AM    = 1.000,
                        AS    = 0.817,
                        ASP   = 0.850,
                        BM    = 0.960,
                        BP    = 0.865,
                        BS    = 0.810,
                        BSP   = 0.851,
                        CAMC = 0.820,
                        CAMS = 0.833,
                        CAMT = 0.812,
                        CM    = 0.891,
                        CP    = 0.848,
                        CS    = 0.809,
                        CSP   = 0.857,
                        DM    = 0.895,
                        DP    = 0.858,
                        DS    = 0.800,
                        DSP   = 0.840,
                        EM    = 0.894,
                        EP    = 0.849,
                        ES    = 0.789,
                        ESP   = 0.836,
                        FM    = 0.907,
                        FP    = 0.863,
                        FS    = 0.803,
                        FSAE  = 0.962,
                        FSP   = 0.824,
                        GS    = 0.788,
                        HCR   = 0.814,
                        HCS   = 0.793,
                        HS    = 0.780,
                        JA    = 0.856,
                        JB    = 0.822,
                        JC    = 0.718,
                        KM    = 0.930,
                        SM    = 0.855,
                        SMF   = 0.841,
                        SS    = 0.821,
                        SSC   = 0.801,
                        SSM   = 0.875,
                        SSP   = 0.853,
                        SSR   = 0.843,
                        STH   = 0.813,
                        STR   = 0.827,
                        STS   = 0.811,
                        STU   = 0.828,
                        STX   = 0.815,
                        XP    = 0.885,)



    @classmethod
    def factor(cls, year, car_class):
        if year == 2018:
            factors = cls.FACTORS_2018
        elif year == 2019:
            factors = cls.FACTORS_2019
        else:
            raise ValueError('Unexpected year')

        car_class = car_class.upper()
        # Remove Ladies designation
        if car_class.endswith('L'):
            car_class = car_class[0:-1]
        factor = factors[car_class]
        return Decimal(str(factor))

