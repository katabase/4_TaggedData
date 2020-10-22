<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="3.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0">
    
    <xsl:output method="text" encoding="UTF-8"/>
    
    <xsl:strip-space elements="*"/>
    
    <xsl:variable name="xmlDocuments" select="collection('?select=?*.xml;recurse=yes')"/>
    
    <xsl:variable name="descs" select="$xmlDocuments//desc[@xml:id]"/>
    
    <xsl:template match="/">
        <xsl:text>Id</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Term</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Term @ana</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Measure</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Measure @type</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Measure @unit </xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Measure @n</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Date</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Date @when</xsl:text>
        <xsl:text>&#09;</xsl:text>
        <xsl:text>Desc</xsl:text>
        <xsl:text>&#10;</xsl:text>
        <xsl:for-each select="$descs">
            <xsl:value-of select="./@xml:id"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./term/text()"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./term/@ana"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./measure/text()"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./measure/@type"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./measure/@unit"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./measure/@n"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./date/text()"/>
            <xsl:text>&#09;</xsl:text>
            <xsl:value-of select="./date/@when"/>
            <xsl:text>&#09;</xsl:text>
            <!-- normalize-space is used because of break-lines inside the desc element. -->
            <xsl:value-of select="normalize-space(.)"/>
            <xsl:text>&#10;</xsl:text>
        </xsl:for-each>
        
    </xsl:template>
    
</xsl:stylesheet>