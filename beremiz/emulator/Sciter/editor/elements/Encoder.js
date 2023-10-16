import { SimElement } from "../sim_elem";   // Класс реализующий логику работы элементов в эмуляторе

const pins = [{name: "A", type: "output", x: 45, y: 5, index: 0}, // конфигурация I/O 
              {name: "B", type: "output", x: 45, y: 10, index: 1}, 
              {name: "Switch", type: "output", x: 45, y: 15, index: 2},
              {name: "Turn_switch", type: "output", x: 45, y: 20, index: 3}]

const SETTINGS = [ {type: "number", parameter_name: "Step", max_value: 100, min_value: 1, step: 1} ]    // Конфигурация настроек элемента

const DEFAULT_ATTRS = {"Step": 3}       // Значения настроек элемента по умолчанию

const DEFAULT_HIGHT = 25;
const DEFAULT_WIDTH = 45;

/** Класс энкодера наследуется от SimElement */
class Encoder extends SimElement{
    // Константа для установки положения энкодера 
    default_rotate = 115;
    /** Конструктор класса параметры передаются в reactor 
     * см. https://github.com/c-smile/sciter-js-sdk/tree/main/docs/md/reactor 
     */ 
    constructor(props, kids){
        // Вызов конструктора родителей
        super(props, kids);

        // Установка I/O
        this.set_connectors(pins);
        // Проверка заданных аттрибутов
        if (this.attrs.length == 0){
             // Установка значений конфигурации по умолчанию     
            this.attrs = DEFAULT_ATTRS;
        }

        // Установка параметров конфигурации окна настроек
        this.settings = SETTINGS;
        // Переменная определяющая положение вала энкодера
        this.rotate = this.default_rotate;
        // Счетчик оборотов вала энкодела
        this.turns = 0;
    }
    /** @brief  Статическая функция для генерации изображения элемента. 
     *          Эта функция должна вызываться без конструктора класса.
     *          Документация на svg формат см. https://developer.mozilla.org/en-US/docs/Web/SVG
     *  @param  width       - ширина svg рисунка.
     *  @param  height      - высота svg рисунка.
     *  @param  className   - зарезервированная переменная для изменения стиля css  
     *  @param  rotate      - угол поворота энкодера. Данная переменная является опциональной служит для конфигурации энкодера
     *  @returns JSX        - виртуальный элемент DOM дерева. См. https://sciter.com/tutorials/reactor-jsx/
    */
    GetSVG()
    {
        return Encoder.get_svg(this.width, this.height, "", this.rotate, false)
    }
    
    static get_svg(width, height, className = '', rotate=115, vision = true){
        
        let zoom_x = 1;
        let zoom_y = 1;
        if (height !== DEFAULT_HIGHT) { zoom_y = height / DEFAULT_HIGHT; }
        if(width !== DEFAULT_WIDTH) { zoom_x = width / DEFAULT_WIDTH; }

        // Переменные для установки положения вала энкодера
        let cx_rotate, cy_rotate;
        // Переменные указывающие
        // центр вала энкодера
        let cx = 17.5  * zoom_x;                                                           
        let cy = 12.5  * zoom_y;

        // радиус вала энкодера
        let r = 9 * zoom_x;

        // вычисление положения вала по углу поворота
        cx_rotate = cx + r * 0.65 * Math.cos(rotate * Math.PI / 180) ;
        cy_rotate = cy + r * 0.65 * Math.sin(rotate * Math.PI / 180);           
        
        let pin_names = []
        if (vision && pins.length > 1)
        {
            for (let pin of pins )
            {
                pin_names.push (<text style={`font-size:${4.2 * zoom_x}px;line-height:1.25;font-family:sans-serif;word-spacing:0px;stroke-width:0.2`}
                x={(pin.x - 5) * zoom_x} y={(pin.y - 1) * zoom_y}>{`${pin.name[0].toUpperCase()}`}</text>)
            }
        }
        
        return (
                <svg style={`background:transparent;`}
                    width={width}
                    height={height}
                    class={className}
                    xmlns="http://www.w3.org/2000/svg"> 
                    <g>
                        {pin_names}
                        <rect
                            style="fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:0.257106;"
                            width={35 * zoom_x}
                            height={25 * zoom_y}
                            x="0"
                            y="0" />
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={5 * zoom_y} x2={45 * zoom_x} y2={5 * zoom_y} stroke="black" />
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={10 * zoom_y} x2={45 * zoom_x} y2={10 * zoom_y} stroke="black" />
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={15 * zoom_y} x2={45 * zoom_x} y2={15 * zoom_y} stroke="black" />
                        <line style="stroke-width: 0.3;" x1={35 * zoom_x} y1={20 * zoom_y} x2={45 * zoom_x} y2={20 * zoom_y} stroke="black" />
                    </g>
                    <g id="rotate">  
                        <circle
                            style={`fill:#ffffff;fill-opacity:1;stroke:#000000;stroke-width:0.264583;`}
                            cx={cx}     
                            cy={cy}
                            r={r}/>
                        <circle style={`fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.264583;`}
                            cx={cx_rotate}
                            cy={cy_rotate}
                            r={1 * zoom_x}/>
                    </g>
                </svg>);
    }
    /** @brief  Метод вызывается при обновлении элемента. 
     *          Обновление элемента происходит при событиях 
     *          от пользователя (перенос элемента, клик по элемента и т.д.)
     *  @returns JSX - виртуальный элемент DOM дерева. См. https://sciter.com/tutorials/reactor-jsx/
     */
    render(){
        return (<div class="draggable unselectable" id={this.target_name} titleid="elements"
                style={`top: ${this.top}; left: ${this.left};`} >
                    {this.connectors}
                    {this.GetSVG()}
                </div>)
    }
    /** @brief  Метод вызывается при событии прокрутки колеса мыши в режиме эмуляции 
     *          Здесь реализован поворот энкодера
     *  @param evt - см. https://developer.mozilla.org/en-US/docs/Web/API/Element/wheel_event
     *  @returns None
    */
    Wheel(evt){
        
        let wheel;
        // Получить пин с именем "A". Имена пинов описаны в константе pins выше
        let connectorA = this.$("div#A");
        // Получить пин с именем "B"   
        let connectorB = this.$("div#B");

        // Определение вращение колеса мыши
        if(evt.deltaY < 0){                   
            wheel = this.attrs.Step;
            // Приращение угла на значение заданное в конфигурации
            this.rotate += wheel;
            // вызов функции установки значения на пин "A"          
            encoder_step(connectorA)
        }else{
            wheel = -this.attrs.Step;         
            this.rotate += wheel;
            encoder_step(connectorB)
        }
        // вычисление количества оборотов
        let turn = Math.floor(this.rotate / 360)
        if (turn !== this.turns){                   
            this.turns = turn;
            // Получить пин с именем "Turn_switch"
            let connector = this.$("div#Turn_switch")
            // Установить значение на выход пина "Turn_switch"
            connector.set_out(1);
            connector.set_out(0);
        }

        /** @brief Функция реализует эмуляцию работы энкодера */
        function encoder_step(conn){
            conn.set_out(1)
            conn.set_out(0)
        }
    }

    /** @brief Событие вызывающееся при нажатии на левую кнопку мыши  
     *  @param evt - см. https://developer.mozilla.org/en-US/docs/Web/API/Element/mousedown_event
     *  @returns None
    */
    MouseDown(evt){
        let connector = this.$("div#Switch")
        connector.set_out(1);
    }

    /** @brief Событие вызывающееся при отжатии левой кнопки мыши  
     *  @param evt - см. https://developer.mozilla.org/en-US/docs/Web/API/Element/mouseup_event
     *  @returns None
    */
    MouseUp(evt){
        let connector = this.$("div#Switch")
        connector.set_out(0);
    }
}
/** Привязка функции к глобальной переменной для вызова из эмулятора
 */
globalThis["Encoder"] = function(param){
    return <Encoder tagname={param.tagname} x={param.x} y={param.y} height={DEFAULT_HIGHT} width={DEFAULT_WIDTH} editor={param.editor} attrs={param.attrs}></Encoder>
}
globalThis["Encoder"].get_svg = Encoder.get_svg;
