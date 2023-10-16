export const path_h = 'H';
export const path_v = 'V';

export function SVG_rect(x, y, width, height, attrs={style:"", id: "", class: "", })
{
  let rect_style = `fill:#ffffff;
                fill-opacity:1;
                fill-rule:evenodd;
                stroke:#000000;
                stroke-linejoin:round;
                stroke-opacity:1;
                paint-order:stroke fill markers;
                ${attrs.style}`
  return <rect id={attrs.id}class={attrs.class} style={rect_style} width={width} height={height} x={x} y={y}/>;
}

export function SVG_text(x, y, px_font_sz, text)
{   
    let text_style = `font-size:${px_font_sz}px;
                      line-height:1.25;
                      font-family:sans-serif;
                      text-align:center;
                      word-spacing:0px;
                      text-anchor:middle;
                      stroke-width:0.264583`;
    return <text style={text_style} x={x} y={y}> {text}</text>;
}

export function SVG_path(startx, end, y, direction, stroke_width=0.3)
{
  let style_text = `stroke-width:${stroke_width}`;
  let x1, x2, y1, y2;
  if (direction == path_h) {
     x1 = startx; x2 = end; y1 = y2 = y;
  }
  else if (direction == path_v) {
    x1 = x2 = startx; y1 = end; y2 = y;
  }
  else{ 
    console.error("path direction Error!");
    return;
  }
  return <line style={style_text} x1={x1} y1={y1} x2={x2} y2={y2} stroke="black" />
}

export function SVG_ellipse(cx, cy, r=2)
{   
  let ellipse_style = `fill:red;
                       fill-opacity:1;
                       fill-rule:evenodd;
                       stroke:#000000;
                       stroke-width:0.86596;
                       stroke-linejoin:round;
                       stroke-opacity:1;
                       paint-order:stroke fill markers`;
  return <ellipse style={ellipse_style} cx={cx} cy={cy} rx={r} ry={r} />;
}