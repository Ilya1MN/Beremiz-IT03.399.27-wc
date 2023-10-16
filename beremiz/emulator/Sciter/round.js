export function round5(x)
{
    return Math.ceil(x/5)*5;
}

export function roundX(x, r){
    //r = Math.round(r);
    return Math.ceil(x/r)*r;
}