import { SimElement } from "../sim_elem";
import { ElementConnector } from "../ElementConnector";

const pins = [{name: "stepper", type: "output", x: 50, y: 15, index: 0}]

const SETTINGS = [  {type: "number", parameter_name: "Step", max_value: 10, min_value: 0, step: 1},
                    {type: "number", parameter_name: "Minimum value", max_value: 200, min_value: -200, step: 0.1},
                    {type: "number", parameter_name: "Maximum value", max_value: 200, min_value: -200, step: 0.1}, ]

const DEFAULT_ATTRS = {"Step": 1, "Minimum value": 0, "Maximum value": 10}

const DEFAULT_HIGHT = 30;
const DEFAULT_WIDTH = 50;

class Stepper extends SimElement{
    constructor(props, kids){
        super(props, kids);
        this.set_connectors(pins);
        if (this.attrs.length == 0){
            this.attrs = DEFAULT_ATTRS;
        }
      
        this.settings = SETTINGS;
        this.set_value = this.attrs["Minimum value"];
        this.use_set_value = false;
    }

    GetSVG() { return Stepper.get_svg(this.width, this.height, '', this.set_value, false); }

    static get_svg(width, height, className = '', set_val = "Nan", visable=true, vision = true){

        let zoom_x = 1;
        let zoom_y = 1;
        if (height !== DEFAULT_HIGHT) { zoom_y = height / DEFAULT_HIGHT; }
        if(width !== DEFAULT_WIDTH) { zoom_x = width / DEFAULT_WIDTH; }

        let text = undefined;
        if (visable) { 
            text =   <g>
                        <rect style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                                width={35 * zoom_x} height={30 * zoom_y}/>
                        <rect style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                                width={25 * zoom_x} height={10 * zoom_y} x={5 * zoom_x} y={10 * zoom_y} />
                        <text style={`font-size:${4.2 * zoom_y}px;line-height:1.25;font-family:sans-serif;word-spacing:0px;stroke-width:0.2`}
                            x={10 * zoom_x} y={17 * zoom_y}>{`${set_val}`}</text>
                        <rect  id="UpValue" style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                                width={5 * zoom_x} height={4 * zoom_y} x={24 * zoom_x} y={11 * zoom_y} />
                        <rect id="DownValue" style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                            width={5 * zoom_x} height={4 * zoom_y} x={24 * zoom_x} y={15 * zoom_y} />
                        <g>
                            <line style="stroke-width: 0.3;" x1={25.5 * zoom_x} y1={13.5 * zoom_y} x2={27.5 * zoom_x} y2={13.5 * zoom_y} stroke="black" />
                            <line style="stroke-width: 0.3;" x1={25.5 * zoom_x} y1={13.5 * zoom_y} x2={26.5 * zoom_x} y2={12 * zoom_y} stroke="black" />
                            <line style="stroke-width: 0.3;" x1={26.5 * zoom_x} y1={12 * zoom_y} x2={27.5 * zoom_x} y2={13.5 * zoom_y} stroke="black" />
                        </g>
                        <g>
                            <line style="stroke-width: 0.3;" x1={25.5 * zoom_x} y1={16 * zoom_y} x2={27.5 * zoom_x} y2={16 * zoom_y} stroke="black" />
                            <line style="stroke-width: 0.3;" x1={25.5 * zoom_x} y1={16 * zoom_y} x2={26.5 * zoom_x} y2={17.5 * zoom_y} stroke="black" />
                            <line style="stroke-width: 0.3;" x1={26.5 * zoom_x} y1={16.5 * zoom_y} x2={27.5 * zoom_x} y2={16 * zoom_y} stroke="black" />
                        </g>
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={15 * zoom_y} x2={50 * zoom_x} y2={15 * zoom_y} stroke="black" />
                    </g>;
        }
        else { 
            text =  <g>
                        <rect style="fill:#ffffff;fill-rule:evenodd;stroke:#000000;stroke-width:0.2;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;paint-order:stroke fill markers"
                                width={35 * zoom_x} height={30 * zoom_y}/>
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={15 * zoom_y} x2={50 * zoom_x} y2={15 * zoom_y} stroke="black" />
                    </g>;
        }
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
                    {pin_names}
                    {text}
                </svg>)
    }

    render(){
        let vdom_el;
        let style_vdom = "position: absolute; left: 5; top: 8; width:25; font-size:4.23333px;";
        //let read_only_set = (this.isReadOnly()) ? true : false;
        vdom_el = <input class="value" type="number" id="setValueInput" name="value" 
                min={this.attrs["Minimum value"]} max={this.attrs["Maximum value"]} step={this.attrs["Step"]} value={this.set_value}
                style={style_vdom} /*readonly={read_only_set}*//>

        

        return (<div class="draggable unselectable" id={this.target_name} titleid="elements"
                style={`top: ${this.top}; left: ${this.left};`} >
                    {this.connectors}
                    {this.GetSVG()}
                    {vdom_el}
                </div>)
    }

    Wheel(evt){
        if(evt.deltaY < 0){
            this.set_value = this.SetValidValue(this.set_value, this.attrs.Step, this.attrs);
        }
        else {
            this.set_value = this.SetValidValue(this.set_value, -this.attrs.Step, this.attrs);
        }
        let connector = this.$("div#stepper");
        connector.set_out(this.set_value);
    }


    SetValidValue(value, step, attrs)
    {
        let set_value = value + step;
        if( (value + step) > attrs["Maximum value"]) { set_value = attrs["Maximum value"]; }
        else if ( (value + step) < attrs["Minimum value"]) { set_value = attrs["Minimum value"]; }
        return set_value;
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


    ["on input at input.value"]( event, input ) {
        if (this.isReadOnly()){

            if (typeof input.value === "number")    { this.set_value = this.SetValidValue(input.value, 0, this.attrs); }

            let connector = this.$("div#stepper");
            connector.set_out(this.set_value);
        }
        else { input.value = this.set_value; }
    }
}



globalThis["Stepper"] = function(param){
    return <Stepper tagname={param.tagname} x={param.x} y={param.y} height={DEFAULT_HIGHT} width={DEFAULT_WIDTH} editor={param.editor} attrs={param.attrs}/>
}
globalThis["Stepper"].get_svg = Stepper.get_svg;
