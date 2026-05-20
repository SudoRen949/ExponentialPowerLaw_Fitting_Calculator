import math
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='./templates')

def fit_exponential(x_data, y_data):
    """Fits y = a * e^(b * x) by linearizing to ln(y) = ln(a) + b*x"""
    n = len(x_data)
    # Linearize y -> Y = ln(y)
    # Handle mathematical guardrail for non-positive values
    for y in y_data:
        if y <= 0:
            return None, None, "Error: Exponential fit requires all Y values to be strictly positive (> 0)."
            
    Y_data = [math.log(y) for y in y_data]
    
    sum_x = sum(x_data)
    sum_Y = sum(Y_data)
    sum_x2 = sum(x**2 for x in x_data)
    sum_xY = sum(x * Y for x, Y in zip(x_data, Y_data))
    
    # Calculate linear regression slope (b) and intercept (ln_a)
    denom = (n * sum_x2 - sum_x**2)
    if denom == 0:
        return None, None, "Error: Vertical line or redundant X points detected."
        
    b = (n * sum_xY - sum_x * sum_Y) / denom
    ln_a = (sum_Y - b * sum_x) / n
    a = math.exp(ln_a)
    
    return a, b, None

def fit_power_law(x_data, y_data):
    """Fits y = a * x^b by linearizing to ln(y) = ln(a) + b*ln(x)"""
    n = len(x_data)
    
    # Handle mathematical guardrails
    for x, y in zip(x_data, y_data):
        if x <= 0 or y <= 0:
            return None, None, "Error: Power-law fit requires all X and Y values to be strictly positive (> 0)."
            
    X_data = [math.log(x) for x in x_data]
    Y_data = [math.log(y) for y in y_data]
    
    sum_X = sum(X_data)
    sum_Y = sum(Y_data)
    sum_X2 = sum(X**2 for X in X_data)
    sum_XY = sum(X * Y for X, Y in zip(X_data, Y_data))
    
    denom = (n * sum_X2 - sum_X**2)
    if denom == 0:
        return None, None, "Error: Redundant X data configuration."
        
    b = (n * sum_XY - sum_X * sum_Y) / denom
    ln_a = (sum_Y - b * sum_X) / n
    a = math.exp(ln_a)
    
    return a, b, None

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    
    # Preserve input fields for better UX
    raw_x = request.form.get('x_data', '')
    raw_y = request.form.get('y_data', '')
    fit_type = request.form.get('fit_type', 'exponential')
    
    if request.method == 'POST':
        try:
            # Safe parsing: split by commas or spaces, strip out garbage text
            x_data = [float(i) for i in raw_x.replace(',', ' ').split() if i.strip()]
            y_data = [float(i) for i in raw_y.replace(',', ' ').split() if i.strip()]
            
            if len(x_data) != len(y_data):
                error = f"Data mismatch error: You provided {len(x_data)} X-values but {len(y_data)} Y-values."
            elif len(x_data) < 2:
                error = "Data density error: At least 2 coordinates are needed to map a regression trend."
            else:
                if fit_type == 'exponential':
                    a, b, err = fit_exponential(x_data, y_data)
                    if err:
                        error = err
                    else:
                        # Construct a dynamic step-by-step breakdown list for the Extra/UI credit
                        equations = [f"y = {a:.4f} \\cdot e^{{{b:.4f}x}}"]
                        result = {"a": round(a, 5), "b": round(b, 5), "equations": equations, "type": "Exponential"}
                else:
                    a, b, err = fit_power_law(x_data, y_data)
                    if err:
                        error = err
                    else:
                        equations = [f"y = {a:.4f} \\cdot x^{{{b:.4f}}}"]
                        result = {"a": round(a, 5), "b": round(b, 5), "equations": equations, "type": "Power-Law"}
                        
        except ValueError:
            error = "Parsing Failure: Please look closely at your data input arrays. Use spaces or commas between normal numbers only."
            
    return render_template('index.html', result=result, error=error, raw_x=raw_x, raw_y=raw_y, fit_type=fit_type)

# Essential wrapper rule for local debugging vs cloud Vercel environment
if __name__ == '__main__':
    app.run(debug=True)
