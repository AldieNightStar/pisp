# Pisp (List like language to Python)

* Uses `pisp_api` library for it's work

# Syntax stuff
* Single call `(func arg1 arg2)`
* Code block (Generates lamda) `(do ... )`
* Code block supports parameter aliasing `(do:i ...)`
    * Or multiple `(do:i,j ...)` (But don't add space between)
* Also we can do shorter codeblocks with `::`. Sample: `(if True :: "OK")`
* Shorter codeblocks supports alasing as well: `(for (range 100) ::i (print i))`
    * Or multiple `::i,j` (But don't add space between)
* Python raw code (As is) `(raw 'print(123)')`
* Comments begin with `#` and `;` also
* Create function `(def name a b c :: ...)`
* Local variable `(local name :: (name "Haxi") (print (name)) )`
    * Use `(name ...)` to set the value. Or alternatively `(name.set ...)`
    * Use `(name)` to get the value. Or alternatively `(name.get)`

