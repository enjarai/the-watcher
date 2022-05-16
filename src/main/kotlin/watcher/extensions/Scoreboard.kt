package watcher.extensions

import com.kotlindiscord.kord.extensions.commands.Arguments
import com.kotlindiscord.kord.extensions.commands.converters.impl.user
import com.kotlindiscord.kord.extensions.extensions.Extension
import com.kotlindiscord.kord.extensions.extensions.publicSlashCommand
import com.kotlindiscord.kord.extensions.types.respond
import watcher.TEST_SERVER_ID

class Scoreboard : Extension() {
    override val name = "scoreboard"

    override suspend fun setup() {
        publicSlashCommand(::ScoreboardArgs) {
            name = "sb"
            description = "View the scoreboard"

            guild(TEST_SERVER_ID)  // Otherwise it'll take an hour to update

            action {
                // Because of the DslMarker annotation KordEx uses, we need to grab Kord explicitly
                val kord = this@Scoreboard.kord

                // TODO: Code to read scoreboard

                respond {
                    content = "Haha, I'm not coded yet"
                    // TODO: Make embed with scoreboard
                }
            }
        }
    }

    inner class ScoreboardArgs : Arguments() {
        val scoreboard by user {
            name = "scoreboard"
            description = "Target scoreboard"
        }
    }
}
