# RandomAttackText

{user} expands to user running the command
{target} expands to the target for the commands, as in `!attack <target>`

If `Level` is set, `User` is ignored, and everyone with the correct permission level can run the command.

Example Config.ini.

```INI
[Attack]
User = nossebro
Response = {user} attacks {target} with {object}!
Object = object 1|an object|objects
```
