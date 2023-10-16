export const plc_output_interfaces = 
{
    DO: {   size: 8,
            function_name: "InterfaceDO",
            modes: {normal: 0, fast: 1, pwm: 2, off: 3}
        },

    AO: {   size: 5,
            function_name: "InterfaceAO",
            modes: {normal: 0, fast: 1, off: 3}
        }
};
export const plm2004 = 
{
    input:
    {
        digit:
        {
            DI: 
            {   size: 8,
                name: "Дискретные входы",
                modes: {normal: 0, count: 1, tachometer: 2, 
                    encoder_cnt: 3, encoder_cntTach: 4}
                
            },
        },
        analog:
        {
            AI: {   
                size: 2,
                name: "Аналоговый вход",
                modes: {poll: 0, off: 2} 
            },
            PT: 
            {   size: 4,
                name: "PT1000",
                modes: {poll: 0, off: 2} 
            },
            DT: {   
                size: 10,
                name: "DS18B20",
                modes: {poll: 0, search: 1,off: 2} 
            },
        }
    },

    output: 
    {
        digit:
        {
            DO: {   
                size: 8,
                name: "Дискретные выходы",
                function_name: "InterfaceDO",
                modes: {normal: 0, fast: 1, pwm: 2, off: 3}
            }
        },
        analog:
        {
            AO: {   
                size: 5,
                name: "Аналоговые выходы",
                function_name: "InterfaceAO",
                modes: {normal: 0, fast: 1, off: 3}
            },
        }
    }
}