import React from 'react'
import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react'
import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <Box pt={16} textAlign="center">
      <VStack spacing={6}>
        <Heading size="2xl">Welcome to Ticket SaaS</Heading>
        <Text fontSize="xl" color="gray.700">
          The easiest way to manage IT support tickets for your organization.
        </Text>
        <Button colorScheme="blue" size="lg" as={Link} to="/dashboard">
          Go to Dashboard
        </Button>
      </VStack>
    </Box>
  )
}