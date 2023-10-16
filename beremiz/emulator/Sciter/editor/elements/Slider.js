import { SimElement } from "../sim_elem";               // Класс реализующий логику работы элементов в эмуляторе


const pins = [{name: "slider", type: "output", x: 50, y: 15, index: 0}] // конфигурация I/O 

const SETTINGS = [  {type: "number", parameter_name: "Step", max_value: 10, min_value: 0, step: 1},                 // Конфигурация настроек элемента
                    {type: "number", parameter_name: "Minimum value", max_value: 200, min_value: -200, step: 0.1},
                    {type: "number", parameter_name: "Maximum value", max_value: 200, min_value: -200, step: 0.1}, ]

const DEFAULT_ATTRS = {"Step": 1, "Minimum value": 0, "Maximum value": 10}      // Значения настроек элемента по умолчанию

const SLIDER_POS_MIN = 2.5;
const SLIDER_POS_MAX = 32.5;

const DEFAULT_HIGHT = 30;
const DEFAULT_WIDTH = 50;

class Slider extends SimElement{                    // Класс элемента наследуется от SimElement
    constructor(props, kids) {                      // Конструктор класса параметры передаются в reactor (см. https://github.com/c-smile/sciter-js-sdk/tree/main/docs/md/reactor)
        super(props, kids);                         // Вызов конструктора класса от которого настедуется Slider
        this.set_connectors(pins);                  // Установка I/O
        if (this.attrs.length == 0){                // Проверка заданных аттрибутов
            this.attrs = DEFAULT_ATTRS;             // Установка значений по умолчанию
        }
        this.out_val = 0;
        this.settings = SETTINGS;                   // Установка параметров конфигурации окна настроек
        this.slider_pos = SLIDER_POS_MIN;           // Значение позиции слайдера 
    }

    GetSVG() { return Slider.get_svg(this.width, this.height, "", this.slider_pos, false); }

    static get_svg(width, height, className = '', slider_pos = 14, vision = true){
        let zoom_x = 1;
        let zoom_y = 1;
        if (height !== DEFAULT_HIGHT) { zoom_y = height / DEFAULT_HIGHT; }
        if(width !== DEFAULT_WIDTH) { zoom_x = width / DEFAULT_WIDTH; }
        
        let pin_names = []
        if (vision && pins.length > 1)
        {
            for (let pin of pins )
            {
                pin_names.push (<text style={`font-size:${4.2 * zoom_x}px;line-height:1.25;font-family:sans-serif;word-spacing:0px;stroke-width:0.2`}
                x={(pin.x - 5) * zoom_x} y={(pin.y - 1) * zoom_y}>{`${pin.name[0].toUpperCase()}`}</text>)
            }
        }

        return (<svg style="background:transparent;"
                width={width}
                height={height}
                class={className}
                xmlns="http://www.w3.org/2000/svg">
                    <g>
                        {pin_names}
                        <rect
                        style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                        width={35 * zoom_x}
                        height={30 * zoom_y}/>
                        <rect
                        style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                        width={30 * zoom_x}
                        height={1.5 * zoom_y}
                        x={SLIDER_POS_MIN * zoom_x}
                        y={14.25 * zoom_y} />
                        <ellipse
                        style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                        cx={slider_pos * zoom_x}
                        cy={15 * zoom_y}
                        rx={2 * zoom_x}
                        ry={2 * zoom_y} />
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={15 * zoom_y} x2={50 * zoom_x} y2={15 * zoom_y} stroke="black" />
                    </g>
                </svg>)
    }
    render(){
        return (<div class="draggable unselectable" id={this.target_name} titleid="elements"
                style={`top: ${this.top}; left: ${this.left};`} >
                    {this.connectors}
                    {this.GetSVG()}
                </div>)
    }
    Wheel(evt){
        let valid_value;
        if(evt.deltaY < 0){
            valid_value = this.SetValidValue(this.out_val, this.slider_pos, this.attrs.Step, this.attrs);
            //this.out_val += this.attrs.Step;
        }
        else {
            valid_value = this.SetValidValue(this.out_val, this.slider_pos, -this.attrs.Step, this.attrs);
            //this.out_val -= this.attrs.Step;
        }

        this.out_val = valid_value.set_value;
        this.slider_pos = valid_value.set_slider_pos;

        let connector = this.$("div#slider")
        

        /*if (this.slider_pos < SLIDER_POS_MIN || this.out_val < this.attrs["Minimum value"]){
            this.slider_pos = SLIDER_POS_MIN;
            this.out_val = this.attrs["Minimum value"];
        }else if(this.slider_pos > SLIDER_POS_MAX || this.out_val > this.attrs["Maximum value"]){
            this.slider_pos = SLIDER_POS_MAX;
            this.out_val = this.attrs["Maximum value"];
        }else{
            this.slider_pos = SLIDER_POS_MIN + (SLIDER_POS_MAX - SLIDER_POS_MIN) / (this.attrs["Maximum value"] - this.attrs["Minimum value"]) * this.out_val;
        }*/
        connector.set_out(this.out_val)
    }

    SetValidValue(value, slider_pos, step, attrs)
    {
        let set_value;
        if (slider_pos < SLIDER_POS_MIN || (value + step) < attrs["Minimum value"]){
            console.log(`ValMin = ${attrs["Minimum value"]}`);
            slider_pos = SLIDER_POS_MIN;
            set_value = attrs["Minimum value"];
        }else if(slider_pos > SLIDER_POS_MAX || (value + step) > attrs["Maximum value"]){
            this.slider_pos = SLIDER_POS_MAX;
            set_value = attrs["Maximum value"];
        }else{
            set_value = (value + step);
            slider_pos = this.setSlider(set_value, attrs["Maximum value"], attrs["Minimum value"]);
            //slider_pos = SLIDER_POS_MIN + (SLIDER_POS_MAX - SLIDER_POS_MIN) / (attrs["Maximum value"] - attrs["Minimum value"]) * (set_value + Math.abs(attrs["Minimum value"]) );
        }
        return {set_value: set_value, set_slider_pos: slider_pos};

    }

    setSlider(set_value, max_val, min_val)
    {
        let slider_pos = SLIDER_POS_MIN + ( ( SLIDER_POS_MAX - SLIDER_POS_MIN ) / ( max_val - min_val ) * (set_value - min_val ) );//+ Math.abs(min_val) ) );
        if (slider_pos < SLIDER_POS_MIN) {slider_pos = SLIDER_POS_MIN; }
        else if(slider_pos > SLIDER_POS_MAX) {slider_pos = SLIDER_POS_MAX; }
        return slider_pos;
    }
            

    settingsIsValid(attrs)
    {
        let error = null;
        if(attrs["Maximum value"] < attrs["Minimum value"] )
        {
            error = @"The maximum and minimum parameters are incorrect\n";
        }
        return error;
    }


}




globalThis["Slider"] = function(param){
    return <Slider tagname={param.tagname} x={param.x} y={param.y} height={DEFAULT_HIGHT} width={DEFAULT_WIDTH} editor={param.editor} attrs={param.attrs}/>
}
globalThis["Slider"].get_svg = Slider.get_svg;

/*
<form>
    <input|hslider #slidersrc min=0 max=100 value=0 />
    <input|integer #sliderval min=0 max=100 value=0 step="10"/>
</form>
*/