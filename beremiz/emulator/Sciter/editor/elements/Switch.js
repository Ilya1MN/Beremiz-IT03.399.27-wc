import { SimElement } from "../sim_elem";
import { ElementConnector } from "../ElementConnector";

const pins = [{name: "switch", type: "output", x: 45, y: 15, index: 0}]


const DEFAULT_HIGHT = 30;
const DEFAULT_WIDTH = 45;


class Switch extends SimElement{
    constructor(props, kids){
        super(props, kids);
        /*for (let pin of pins){
            this.connectors.push(
            <ElementConnector target={this.target}
                index={pin.index} 
                id_name={`${pin.name}`} 
                x={pin.x} 
                y={pin.y} 
                interface={pin.type}>
            </ElementConnector>)
        }*/
        this.set_connectors(pins);
        this.switch_pos = false
    }

    GetSVG() { return Switch.get_svg(this.width, this.height, "", this.switch_pos, false) }

    static get_svg(width, height, className = '', switch_pos=false, vision = true){
        
        let zoom_x = 1;
        let zoom_y = 1;
        if (height !== DEFAULT_HIGHT) { zoom_y = height / DEFAULT_HIGHT; }
        if(width !== DEFAULT_WIDTH) { zoom_x = width / DEFAULT_WIDTH; }

        let cx = (switch_pos) ? 26.5 : 11.5;

        let pin_names = []
        if (vision && pins.length > 1)
        {
            for (let pin of pins )
            {
                pin_names.push (<text style={`font-size:${4.2 * zoom_x}px;line-height:1.25;font-family:sans-serif;word-spacing:0px;stroke-width:0.2`}
                                                x={(pin.x - 5) * zoom_x} y={(pin.y - 1) * zoom_y}>{`${pin.name[0].toUpperCase()}`}</text>)
            }
        }

        return(<svg style="background:transparent;"
                        class={className}
                        width={width}
                        height={height}
                        xmlns="http://www.w3.org/2000/svg">
                    <g>
                        {pin_names}
                        <rect
                        style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:0.257106;stroke-opacity:1"
                        width={35 * zoom_x}
                        height={30 * zoom_y}/>
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={15 * zoom_y} x2={45 * zoom_x} y2={15 * zoom_y} stroke="black" />
                        <g>
                            <rect id="input"
                            style="fill:none;fill-opacity:1;stroke:#000000;stroke-width:0.265;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
                            width={25 * zoom_x}
                            height={10 * zoom_y}
                            x={6.5 * zoom_x}
                            y={10 * zoom_y} rx={5 * zoom_x}/>
                            <circle id="input"
                            style="fill:#bababa;fill-opacity:1;stroke:#000000;stroke-width:0.264999;stroke-linecap:butt;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
                            cx={cx * zoom_x}
                            cy={15 * zoom_y}
                            r={5 * zoom_x} />
                        </g>
                    </g>
                </svg>);
    }
    render(){
        return (<div class="draggable unselectable" id={this.target_name} titleid="elements"
                style={`top: ${this.top}; left: ${this.left};`} >
                    {this.connectors}
                    {this.GetSVG()}
                </div>)
    }
    Click(evt){
        console.log("switch click");
        this.switch_pos = !this.switch_pos;
        let connector = this.$("div#switch")
        connector.set_out(this.switch_pos);
    }
}


globalThis["Switch"] = function (param) {
  return <Switch tagname={param.tagname} x={param.x} y={param.y} height={DEFAULT_HIGHT} width={DEFAULT_WIDTH} editor={param.editor} attrs={param.attrs}></Switch>
};
globalThis["Switch"].get_svg = Switch.get_svg;
