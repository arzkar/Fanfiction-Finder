from __future__ import annotations

import asyncio

import discord
from discord.ext import commands
from loguru import logger

from utils.metadata import ao3_metadata, fichub_metadata


class Link(commands.Cog):
    # TODO: Reimplement reaction-based removal for the messages resulting from these commands or consider alternatives.
    #       Maybe send a persistent view with a removal button?
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.hybrid_command()
    @commands.guild_only()
    async def linkao3(self, ctx: commands.Context[commands.Bot], *, query: str) -> None:
        """Command to search AO3. Fallback to Fichub if not found in AO3."""

        # Known at runtime
        assert isinstance(ctx.channel, discord.abc.GuildChannel)

        logger.info("linkao3 command was used. Searching ao3")
        async with ctx.typing():
            logger.info("Sleeping for 1s to avoid ratelimit")
            await asyncio.sleep(1)

            # Run the blocking scrape in a thread so gateway heartbeats keep flowing.
            embed_pg = await asyncio.to_thread(ao3_metadata, query)

            if embed_pg is None:  # if not found in AO3, search in Fichub
                logger.info("Fanfiction not found in AO3, trying to search Fichub")
                embed_pg = await asyncio.to_thread(fichub_metadata, query)

            logger.info(f"Sending embed to Channel-> {ctx.guild}:{ctx.channel.name}")
            if embed_pg:
                await ctx.reply(embed=embed_pg, mention_author=False)

    @commands.hybrid_command()
    @commands.guild_only()
    async def linkfic(self, ctx: commands.Context[commands.Bot], *, query: str) -> None:
        """Command to search Fichub. Fallback to AO3 if not found in AO3."""

        # Known at runtime
        assert isinstance(ctx.channel, discord.abc.GuildChannel)

        logger.info("linkfic command was used. Searching Fichub")
        async with ctx.typing():
            logger.info("Sleeping for 1s to avoid ratelimit")
            await asyncio.sleep(1)

            # Run the blocking scrape in a thread so gateway heartbeats keep flowing.
            embed_pg = await asyncio.to_thread(fichub_metadata, query)

            if embed_pg is None:  # if not found in Fichub, search in AO3
                logger.info("Fanfiction not found in Fichub, trying to search AO3")
                embed_pg = await asyncio.to_thread(ao3_metadata, query)

            logger.info(f"Sending embed to Channel-> {ctx.guild}:{ctx.channel.name}")
            if embed_pg:
                await ctx.reply(embed=embed_pg, mention_author=False)


async def setup(client: commands.Bot):
    await client.add_cog(Link(client))
