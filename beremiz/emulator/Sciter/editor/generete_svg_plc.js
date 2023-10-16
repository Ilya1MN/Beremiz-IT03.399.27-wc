
import { SimElement } from "sim_elem";
import { ElementConnector } from "ElementConnector"
import { SVG_ellipse, SVG_path, SVG_rect, SVG_text, path_h, path_v } from "./svg";
import { GetTarget } from "../storage";
import { zoom_array, get_zoom } from "./editor";

const bitrage = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200];
const mode = ["Slave","Master"];
const ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12", "COM13", "COM14", "COM15"];
const byte_order = ["3210", "0123", "1032", "2301"];

const SETTINGS = [{type: "drop_list", parameter_name: "COM port", options: ports, get_params_callback: ()=>{return Window.this.xcall("GetListComPorts")}},
                  {type: "drop_list", parameter_name: "Bitrate speed", options: bitrage},
                  {type: "radio_button", parameter_name: "Mode", options: mode},
                  {type: "radio_button", parameter_name: "Byte order", options: byte_order},
                  {type: "number", parameter_name: "Slave ID", value: 1, max_value: 247, min_value: 1, step: 1},]

const DEFAULT_ATTRS = {"COM port": "", "Bitrate speed": 9600, "Mode": "Slave", "Byte order": "0123", "Slave ID": 1}

const bias_x = 0;
const bias_y = 1;

const connector_w_h = 4;

const ch_value_font = 4.23333;
const ch_type_font  = 4;
const target_font   = 5.64444;

const rect_y            = bias_y + 12;
const rect_width        = 48;

const rect_val_height    = 7;
const rect_val_width     = 24;
const text_x = 4;
const text_y = bias_y + 17;

/* INPUTS */
const rect_input_x      = bias_x + 8;

    /* Channel DI */
    const DI_interface = {
      ellipse: SVG_ellipse,
      ellipsex: bias_x + 16, 
      ellipsey: bias_y + 24,
      rect_x: bias_x + 30,
      rect_y: bias_y + 21,
      rect_width: rect_val_width,
      rect_height: rect_val_height,
      text_x: bias_x + 32,
      text_y: bias_y + 26,
      text_ch_name: bias_x + 20,//ch_text
      path_startx: bias_x + 0,
      path_endx: bias_x + 14,
      path_y: bias_y + 24,
      w_h: connector_w_h,
    };
    

    /* Channel AI */
    const AI_interface = {
      rect_x: bias_x + 10,
      rect_y: bias_y + 20,
      rect_width: rect_val_width,
      rect_height: rect_val_height,
      text_x: bias_x + 12,
      text_y: bias_y + 25,
      text_ch_name: bias_x + 38,//ch_text
      path_startx: bias_x + 0,
      path_endx: bias_x + 10,
      path_y: bias_y + 24,
      w_h: connector_w_h,
    };

/* OUTPUTS */
const rect_output_x      = bias_x + 64;
  /* Channel DO */
    const DO_interface = {
      ellipse: SVG_ellipse,
      ellipsex: bias_x + 106, 
      ellipsey: bias_y + 24,
      rect_x: bias_x + 66,
      rect_y: bias_y + 21,
      rect_width: rect_val_width,
      rect_height: rect_val_height,
      text_x: bias_x + 68,
      text_y: bias_y + 26,
      text_ch_name: bias_x + 91,//ch_text
      path_startx: bias_x + 120,
      path_endx: bias_x + 108,
      path_y: bias_y + 24,
      w_h: connector_w_h,
    };
    /* Channel AO */
    const AO_interface = {
      rect_x: bias_x + 86,
      rect_y: bias_y + 20,
      rect_width: rect_val_width,
      rect_height: rect_val_height,
      text_x: bias_x + 88,
      text_y: bias_y + 25,
      text_ch_name: bias_x + 74,//ch_text
      path_startx: bias_x + 120,
      path_endx: bias_x + 110,
      path_y: bias_y + 24,
      w_h: connector_w_h,
    };

/* Plc */
const plc_rect_x            = bias_x + 4;
const plc_rect_y            = bias_y + 0;
const plc_rect_width        = 112;

const plc_path_hstartx      = bias_x + 4;
const plc_path_hendx        = bias_x + 114;
const plc_path_hy           = bias_y + 8;

const plc_path_vstartx      = bias_x + 59;
const plc_path_vy           = bias_y + 8;

const plc_rect_sett_x       = bias_x + 102;
const plc_rect_sett_y       = bias_y + 2;
const plc_rect_sett_width   = 9;
const plc_rect_sett_height  = 4;

const plc_text_x            = bias_x + 10;
const plc_text_y            = bias_y + 6;

export class Plc extends SimElement {
  constructor(props, kids, parent) {
    super(props, kids, parent);
    this.max_height_in  = 0;
    this.max_height_out = 0;
    this.max_h_in  = {max: this.max_height_in};
    this.max_h_out = {max: this.max_height_out};
    this.target_plc = GetTarget(this.target_name);
    this._input_api = Window.this.xcall("GetInputNativeApi");
    
    this.plc_input_channels = this.set_i_o_interface("input", rect_input_x, this.max_h_in);

    this.plc_output_channels = this.set_i_o_interface("output", rect_output_x, this.max_h_out);

    if (this.height === undefined){
      this.height = Math.max(this.max_h_in.max, this.max_h_out.max) + 15;
    }

    if (this.attrs.length == 0){
      this.attrs = DEFAULT_ATTRS;
    }

    this.settings = SETTINGS;
    if (globalThis["MbrtuStatusClass"]) { 
      this.MbrtuStatus = globalThis["MbrtuStatusClass"]; 
      this.MbrtuStatus.setEditorFlag(true);
      this.MbrtuStatus.SetData(this.attrs["COM port"], this.attrs["Mode"])
  }

  else { this.MbrtuStatus = undefined; }
  //console.log(this.MbrtuStatus);
}

//destructor
oncloserequest(evt)
{
  if(this.MbrtuStatus)
  {
    console.log("close editor");
    this.MbrtuStatus.setEditorFlag(false);
  }
}

  set_i_o_interface(direction, rect_sz_z, max_h){
    const set_default_value = "Nan"
    let i_o = this.target_plc[direction];
    if(i_o)
    {
      let input_interfaces = []
      if(i_o?.digit)
      {
        for(let plc_io in i_o.digit)
        {
          let interface_box_sizes = (direction === "input") ? DI_interface : DO_interface
          let set = {digit: interface_box_sizes, name: i_o.digit[plc_io].name, value: set_default_value, sz: i_o.digit[plc_io].size}
          input_interfaces.push(this.GenerateInterface(direction, set.digit, set.name, max_h, set_default_value, 
            rect_sz_z, plc_io, set.sz))
        }
      }
      if(i_o?.analog)
      {
        for (let plc_io in i_o.analog)
        {
          let interface_box_sizes = (direction === "input") ? AI_interface : AO_interface
          let set = {analog: interface_box_sizes, name: i_o.analog[plc_io].name, value: set_default_value, sz: i_o.analog[plc_io].size}
          input_interfaces.push(this.GenerateInterface(direction, set.analog, set.name, max_h, set_default_value,
            rect_sz_z, plc_io, set.sz))
        }
      }
      
      return input_interfaces;
    }
  }

  static InterfaceAO(pin_num, params){
    let frame_editor = document.$("frame#editor")
    let editor = frame_editor.frame.document.$("#editor_app");
    let plc = editor.$(`div#${editor.get_target_name()}`);
    plc.Change_AO_Interface(pin_num, params);
  }

  set_settings(){
    /** Set settings com-port from modbus.
     * Get parameters from arguments string
     * Flags: -b - BaudRate  = 0..7
     *        -d - DataBits  = 0..1
     *        -p - Parity    = 0..2
     *        -s - StopBits  = 0..1
     *        -m - Mode      = 0..1
     *        -o - ByteOrder = 0..3
     *        -c - COM port
     *        -i - SlaveID   = 0..247
     * @return Exception code.
     * example: -b 1 -d 0 -p 2 -s 1 -m 0 -o 3
    */
    if(typeof(this.attrs) == "object")
    {
      let com_port_number = Number(this.attrs["COM port"].replace("COM", ""))
      //let com_port_number = ports.indexOf(this.attrs["COM port"]) + 1
      let baudrate_index = bitrage.indexOf(Number(this.attrs["Bitrate speed"]))
      let mode_index = mode.indexOf(this.attrs.Mode)
      let byte_order_index = byte_order.indexOf(this.attrs["Byte order"])
      let slave_id = this.attrs["Slave ID"]
      if (com_port_number !== 0)
      {
        let str = `Soft_Plc -b ${baudrate_index} -d 0 -p 0 -s 0 -m ${mode_index} -o ${byte_order_index} -c ${com_port_number} -i ${slave_id}`
        this.MbrtuStatus.SetData(this.attrs["COM port"], this.attrs["Mode"])
        Window.this.xcall("SetPlcSettingsSciter", str);
      }
    }
  }

  Change_AO_Interface(pin_num, params){
    if(this.target_plc?.output?.analog?.AO?.size)
    {
      if(pin_num <= this.target_plc.output.analog.AO.size)
      {
        const AO_FAST_MODE = this.target_plc.output.analog.AO.modes.fast;
        let container = this.$("g#AO");
        let pin = container.$(`#${pin_num}`)
        if(pin.textVal != params.value)
        {
          if(params.mode <= AO_FAST_MODE)
          {
            pin.textVal = params.value.toFixed(2);
            pin.textVal = Math.floor(pin.textVal * 100) / 100;
          }
          else if(pin.textVal != "Nan"){
            pin.textVal = "Nan";
          }
          pin.componentUpdate();
          let connector = this.$(`div#AO${pin_num}`)
          if(pin.textVal !== "Nan"){
            if (connector){
              if(connector.interface){
                connector.interface(params.value.toFixed(2))
              }
            }
          }
        }
      }
    }
  }

  static InterfaceDO(pin_num, params){
    let frame_editor = document.$("frame#editor")
    let editor = frame_editor.frame.document.$("#editor_app");
    let plc = editor.$(`div#${editor.get_target_name()}`);
    plc.Change_DO_Interface(pin_num, params);
  }

  ondblclick(evt){
    if(this.element_settings()){
      this.set_settings();
    }
    return true;
  }

  Change_DO_Interface(pin_num, params){
    if(this.target_plc?.output?.digit?.DO?.size)
    {
      if(pin_num <= this.target_plc.output.digit.DO.size)
      {
        const YAPLC_DO_MODE_PWM = this.target_plc.output.digit.DO.modes.pwm;
        let container = this.$("g#DO");
        let pin = container.$(`#${pin_num}`);
        let ellipse = pin.$("ellipse")
        
        if(ellipse)
        {
          if(ellipse.style.fill)
          {
            if(pin.textVal != params.value)
            {
              if (params.mode < YAPLC_DO_MODE_PWM)
              {
                pin.textVal = params.value;
                ellipse.style.fill = (pin.textVal % 2) ? "red": "white";
              }
              else if (params.mode === YAPLC_DO_MODE_PWM)
              {
                if (params.status.OEPWM)
                {
                  pin.textVal = `${params.status.OTPWM}, ${params.status.ODPWM}%`;
                  ellipse.style.fill = "blue";
                }else{
                  pin.textVal = "0";
                  ellipse.style.fill = "white";
                }
                
              }
              else if(pin.textVal != "Nan" || ellipse.style.fill != "white")
              {
                pin.textVal = "Nan";
                ellipse.style.fill = "white";
              }
              pin.componentUpdate();
              if(pin.textVal !== "Nan"){
                let connector = this.$(`div#DO${pin_num}`)
                if (connector){
                  if(connector.interface){
                    connector.interface(params.value)
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  Change_DI_Interface(pin_num, set_value){
    if(this.target_plc?.input?.digit?.DI?.size){
      if(pin_num <= this.target_plc.input.digit.DI.size){
        let container = this.$("g#DI");
        let pin = container.$(`#${pin_num}`);
        let ellipse = pin.$("ellipse")
        if(ellipse) {
          if(ellipse.style.fill) {
            if(pin.textVal != set_value) {
              pin.textVal = set_value;
              ellipse.style.fill = (pin.textVal % 2) ? "red": "white";
              pin.componentUpdate();
            }
          }
        }
      }
    }
  }

  Change_AI_Interface(pin_num, set_value, name){
    if(this.target_plc?.input?.analog[name]?.size)
    {
      if(pin_num <= this.target_plc.input.analog[name].size)
      {
        let container = this.$(`g#${name}`);
        let pin = container.$(`#${pin_num}`)
        if(pin.textVal != set_value)
        {
          pin.textVal = set_value.toFixed(2);
          //pin.textVal = Math.floor(pin.textVal * 100) / 100;
          pin.componentUpdate();
        }
      }
    }
  }

  get_interfaces_name(direction){
    let digit_name = [];
    let analog_name = [];

    let i_o_interface = this.target_plc[direction]
    if(i_o_interface?.digit){
      digit_name = get_names(i_o_interface.digit)
    }
    if(i_o_interface?.analog){
      analog_name = get_names(i_o_interface.analog)
    }
    return [...digit_name, ...analog_name];

    function get_names(input_interface){
      let arr = []
      if(input_interface){
        for (let name in input_interface){
          arr.push(name);
        }
      }
      return arr;
    }
  }

  input_set(name, id, set_val, update=false){
    if(!update)
    {
      this._input_api[name].set(id, set_val);
    } 
    
    let value = this._input_api[name].get(id);
    
    if(name === "DI"){
      this.Change_DI_Interface(id, value);
    }
    else {
      this.Change_AI_Interface(id, value, name);
    }
  }

  GenerateInterface(direction, def_interface, channal_name, hight, value, Rect_x, id_name, size)
  {
    let height = 17 - 8 + size*10;
    let plc_interface = new Array();
    let ellipsex = def_interface.ellipsex;
    let ellipsey = def_interface.ellipsey;
    for (let i = 0; i < size; i++)
    {
      let y = i * 10 + hight.max;
      plc_interface.push(<Plc_Channel index={i}
                                 id_name     = {id_name}
                                 rect_x      = {def_interface.rect_x}
                                 rect_y      = {def_interface.rect_y + y}
                                 rect_w      = {def_interface.rect_width}
                                 rect_h      = {def_interface.rect_height}
                                 text_x      = {def_interface.text_x}
                                 text_y      = {def_interface.text_y + y}
                                 ch_name_x   = {def_interface.text_ch_name}
                                 value       = {value}
                                 path_startx = {def_interface.path_startx}
                                 path_endx   = {def_interface.path_endx}
                                 path_y      = {def_interface.path_y + y}
                                 api         = {this._input_api[id_name]}
                                 parent      = {this}>
                      {(def_interface.ellipse) ? def_interface.ellipse(ellipsex, ellipsey + y) : undefined}
                    </Plc_Channel>);
      this.connectors.push(<ElementConnector target={this.target}
                                      index={i} interface_name={id_name}
                                      id_name={`${id_name}${i}`} 
                                      x={def_interface.path_startx} 
                                      y={def_interface.path_y + y}
                                      element={this}
                                      api={this._input_api[id_name]}
                                      interface={direction}>
                          </ElementConnector>);
    }
    let res = <PlcCh_IO id_name= {id_name}
                      rect_x={Rect_x} 
                      rect_y={hight.max + rect_y} 
                      rect_width={rect_width} 
                      rect_height={height} 
                      text_x={Rect_x + text_x} 
                      text_y={hight.max + text_y} 
                      value={channal_name}
                      api={this._input_api}>
              {plc_interface}
            </PlcCh_IO>;
    hight.max += height + 6;
    return res;
  }

  UpdateAllConnectors()
  {
      for(let connector of this.$$("div.connector") )
      {
          connector.set_out_last_value();
      }
      this.set_settings();
  }

  render() {
    return (
      <div  class="draggable unselectable plc" titleid="elements"
            style={this.get_style()}
            id={this.target_name}>
      {this.connectors}
      <svg style="background:transparent;"
        width={120 + (bias_x * 2)}
        height={this.height + (bias_y * 2)}
        xmlns="http://www.w3.org/2000/svg" >
        <g>
        {SVG_rect(plc_rect_x, plc_rect_y, plc_rect_width, this.height, {style: `fill:#1da511;height:${this.height}`, class:"", id:""})}

        {SVG_path(plc_path_hstartx, plc_path_hendx, plc_path_hy, path_h)}

        {SVG_path(plc_path_vstartx, this.height + bias_y, plc_path_vy, path_v)}
        <rect
            id="settings_plc"
            
            style="fill:#ffffff;fill-opacity:1;fill-rule:evenodd;stroke:#000000;stroke-width:0.5;stroke-linejoin:round;stroke-opacity:1;paint-order:stroke fill markers;"
            width={plc_rect_sett_width}
            height={plc_rect_sett_height}
            rx="1"
            x={plc_rect_sett_x}
            y={plc_rect_sett_y}/>
        {SVG_text(plc_text_x, plc_text_y, target_font, this.target_name)}
        {this.plc_input_channels}
        {this.plc_output_channels}
        </g>
      </svg>
      </div>
    );
  }

  SetImageData(zoom)
    {
        let i = zoom_array.indexOf(zoom)
        if(typeof(i) === "number") { 
          this.image[i] = new Graphics.Image(this); 
        }
    }
    //gc();
}

class PlcCh_IO extends Element
{
  constructor(props, kids, parent)
  {
    super();
    this.kids = kids;
    this.plc_ai_rectx = props.rect_x
    this.plc_ai_recty = props.rect_y;
    this.plc_ai_rectwidth = props.rect_width;
    this.plc_ai_rectheight = props.rect_height;
    this.plc_ai_textx = props.text_x;
    this.plc_ai_texty = props.text_y;
    this.plc_ai_text = props.value;
    this.id_name = props.id_name;
    let api = props.api[props.id_name]
    if (api)
    {
      this.set = api.set; //function (ChNum, SetValue)
      this.get = api.get; //function (ChNum) - returned channel value
    }
  }

  render()
  {
    return  <g id={this.id_name}>
              {SVG_rect(this.plc_ai_rectx, this.plc_ai_recty, this.plc_ai_rectwidth, this.plc_ai_rectheight)}
              {SVG_text(this.plc_ai_textx, this.plc_ai_texty, ch_type_font, this.plc_ai_text)}
              {this.kids}
            </g>
  }
}

class Plc_Channel extends Element
{
    constructor(props, kids, parent)
    {
        super();
        this.ellipse      = kids;
        this.index        = props.index;
        this.rectx        = props.rect_x;
        this.recty        = props.rect_y;
        this.rectwidth    = props.rect_w;
        this.rectheight   = props.rect_h;
        this.textx        = props.text_x;
        this.texty        = props.text_y;
        this.textVal      = props.value;
        this.pathstx      = props.path_startx;
        this.pathendx     = props.path_endx;
        this.pathy        = props.path_y;
        this.api          = props.api;
        this.ch_name_x    = props.ch_name_x;
        this.id_name      = props.id_name;
        this.parent       = props.parent
        //this.ElementConnector = null;
    }

  Generate_Channel(i)
  {
    return <g id={i}>
            {this.ellipse}
            {SVG_rect(this.rectx, this.recty, this.rectwidth, this.rectheight)}
            {SVG_text(this.ch_name_x, this.texty, ch_value_font, this.id_name + i )}
            {SVG_text(this.textx, this.texty, ch_value_font, this.textVal)}
            {SVG_path(this.pathstx, this.pathendx, this.pathy, path_h)}
          </g>
  }

  componentDidMount() { // instance of the class is attached to real DOM
    this.timer(200, () => {
      if (this.api)
      {
        let editor = document.body.$("#editor_app");
        if(editor.read_only)
        {
          if(this.api.get) {
            
            let val = this.api.get(this.index);
            this.parent.input_set(this.id_name, this.index, val, true);
          }
          else {this.ElementConnector = null;}
        }
        else if (this.ElementConnector != null) { this.ElementConnector = null; }
      }
      return true; // to keep the timer ticking
    });
  }

  render()
  {
    return this.Generate_Channel(this.index);
  }
}

//var editor = document.$("#editor_app");
/**/
//editor.componentUpdate();

globalThis["Plc"] = function (param) {
  return <Plc tagname={param.tagname} x={param.x} y={param.y} height={param.height} width={param.width} editor={param.editor} attrs={param.attrs} plc_name={param.plc_name}></Plc>
};